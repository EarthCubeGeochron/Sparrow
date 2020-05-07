from click import secho
from sqlalchemy import text
from datetime import datetime
from pathlib import Path
from os import environ
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect

from .util import (
    md5hash, SparrowImportError,
    ensure_sequence, coalesce_nan
)
from ..util import relative_path

class BaseImporter(object):
    """
    A basic Sparrow importer to be subclassed.
    """
    authority = None
    file_type = None
    def __init__(self, db, **kwargs):
        self.db = db
        self.m = self.db.model
        print_sql = kwargs.pop("print_sql", False)
        self.verbose = kwargs.pop("verbose", False)
        # We shouldn't have to do this,
        #self.db.automap()

        # This is kinda unsatisfying
        self.basedir = environ.get("SPARROW_DATA_DIR", None)

        # Allow us to turn of change-tracking for speed
        self.__dirty = set()
        self.__new = set()
        self.__deleted = set()
        @event.listens_for(self.db.session, 'before_flush')
        def on_before_flush(session, flush_context, instances):
            self.__dirty |= set(session.dirty)
            self.__new |= set(session.new)
            self.__deleted |= set(session.deleted)

        @event.listens_for(self.db.session, 'after_commit')
        def on_after_commit(session):
            self.__dirty = set()
            self.__new = set()
            self.__deleted = set()

        if print_sql:
            @event.listens_for(self.db.engine, 'after_cursor_execute', named=True)
            def receive_after_cursor_execute(**kw):
                statement = kw.pop('statement')
                if statement.startswith("SELECT"): return
                secho(str(statement).strip())

        if self.file_type is not None:
            v = self.db.get_or_create(self.m.data_file_type, id=self.file_type)
            self.add(v)
            self.db.session.commit()

        # Deprecated
        self.models = self.m

    def session_changes(self):
        changed = lambda i: self.db.session.is_modified(i, include_collections=True)
        # Bug: For some reason, changes on many-to-many links are not recorded.
        return dict(
            dirty=self.__dirty,
            modified=set(i for i in set(self.__dirty) if changed(i)),
            new=self.__new,
            deleted=self.__deleted)

    def add(self, *models):
        for model in models:
            self.db.session.add(model)

    ###
    # Helpers to insert various types of analytical data
    ###
    def sample(self, **kwargs):
        return self.db.get_or_create(self.m.sample, **kwargs)

    def location(self, lon, lat):
        return f"SRID=4326;POINT({lon} {lat})"

    def publication(self, doi, title=None):
        return self.db.get_or_create(
            self.m.publication,
            doi=doi, defaults=dict(title=title))

    def project(self, name):
        return self.db.get_or_create(self.m.project, name=name)

    def researcher(self, **kwargs):
        return self.db.get_or_create(self.m.researcher, **kwargs)

    ## Vocabulary

    def unit(self, id, description=None):
        u = self.db.get_or_create(
            self.m.vocabulary_unit,
            id=id, defaults=dict(authority=self.authority))
        if u is not None:
            u.description = description
        return u

    def error_metric(self, id, description=None):
        if not id: return None
        em = self.db.get_or_create(
            self.m.vocabulary_error_metric,
            id=id, defaults=dict(authority=self.authority))
        if description is not None:
            em.description = description
        return em

    def parameter(self, id, description=None):
        p = self.db.get_or_create(
            self.m.vocabulary_parameter,
            id=id, defaults=dict(authority=self.authority))
        if description is not None:
            p.description = description
        return p

    def method(self, id):
        return self.db.get_or_create(
            self.m.vocabulary_method,
            id=id, defaults=dict(authority=self.authority))

    def material(self, id, type_of=None):
        if id is None: return None
        m = self.db.get_or_create(
            self.m.vocabulary_material,
            id=id, defaults=dict(authority=self.authority))
        if type_of is not None:
            m._material = self.material(type_of)
        return m

    def analysis_type(self, id, type_of= None):
        m = self.db.get_or_create(
            self.m.vocabulary_analysis_type,
            id=id,
            defaults=dict(authority=self.authority))
        if type_of is not None:
            m._analysis_type = self.analysis_type(type_of)
        return m

    def datum_type(self, parameter, unit='unknown', error_metric=None, **kwargs):
        error_metric = self.error_metric(error_metric)
        try:
            error_metric_id = error_metric.id
        except AttributeError:
            error_metric_id = None

        unit = self.unit(unit)

        # Error values are *assumed* to be at the 1s level, apparently
        parameter = self.parameter(parameter)

        dt =  self.db.get_or_create(
            self.m.datum_type,
            parameter=parameter.id,
            error_metric=error_metric_id,
            unit=unit.id,
            **kwargs)
        return dt

    def analysis(self, type=None, **kwargs):
        if type is not None:
            type = self.analysis_type(type).id
        m = self.db.get_or_create(
            self.m.analysis, analysis_type=type, **kwargs)
        return m

    def add_analysis(self, session, type=None, **kwargs):
        """Deprecated"""
        return self.analysis(session_id=session.id, type=type, **kwargs)

    def attribute(self, analysis, parameter, value):
        if value is None:
            return None
        self.db.session.flush()
        param = self.parameter(parameter)
        attr = self.db.get_or_create(self.m.attribute,
            parameter=param.id,
            value=value)
        analysis.attribute_collection.append(attr)
        return attr

    def datum(self, analysis, parameter, value, error=None, **kwargs):
        value = coalesce_nan(value)
        if value is None:
            return None
        type = self.datum_type(parameter, **kwargs)
        self.db.session.flush()
        datum = self.db.get_or_create(self.m.datum,
            analysis=analysis.id,
            type=type.id)
        datum.value = value
        datum.error = error
        return datum

    def constant(self, analysis, parameter, value, error=None, **kwargs):
        args = dict()
        value = coalesce_nan(value)
        if value is None:
            return None
        type = self.datum_type(parameter, **kwargs)
        self.db.session.flush()
        const = self.db.get_or_create(self.m.constant,
            value=value,
            error=error,
            type=type.id
        )
        analysis.constant_collection.append(const)
        self.db.session.flush()
        return const

    ###
    # Data file importing
    ###

    def warn(self, message):
        secho(str(message), fg='yellow')

    def import_datafile(self, fn, rec, **kwargs):
        raise NotImplementedError()

    def delete_session(self, rec):
        """
        Delete session(s) and associated analysis and datum records,
        given a data file model
        """
        fn = relative_path(__file__, 'sql', 'delete-session.sql')
        sql = text(open(fn).read())
        self.db.session.execute(sql, {'file_hash': rec.file_hash})

    def iterfiles(self, file_sequence, **kwargs):
        """
        This file iterator tracks files in the *data_file* table,
        checks if they have been imported, and potentially imports
        if needed.
        """
        for fn in file_sequence:
            secho(str(fn), dim=True)
            self.__import_datafile(fn, None, **kwargs)

    def __set_file_info(self, infile, rec):
        _ = infile.stat().st_mtime
        mtime = datetime.utcfromtimestamp(_)
        rec.file_mtime = mtime
        rec.basename = infile.name

    def __create_data_file_record(self, fn):

        # Get the path location (this must be unique)
        infile = Path(fn)
        if self.basedir is not None:
            infile = infile.relative_to(self.basedir)
        file_path = str(infile)

        # Get file hash
        hash = md5hash(str(fn))
        # Get data file record if it exists
        rec = (self.db.session.query(self.m.data_file)
                .filter_by(file_path=file_path)).first()

        added = rec is None
        if added:
            rec = self.m.data_file(
                file_path=file_path,
                file_hash=hash)

        updated = rec.file_hash != hash
        if updated:
            rec.file_hash = hash

        rec.file_type = self.file_type

        self.db.session.add(rec)

        self.__set_file_info(fn, rec)
        return rec, added

    def __import_datafile(self, fn, rec=None, **kwargs):
        """
        A wrapper for data file import that tracks data files through
        the import process and builds links to data file types.
        """
        redo = kwargs.pop("redo", False)
        added = False
        if rec is None:
            rec, added = self.__create_data_file_record(fn)

        err_filter = True
        m = self.m.data_file_link
        if kwargs.pop("fix_errors", False):
            err_filter = m.error.is_(None)
        prev_imports = (
            self.db.session
                .query(m)
                .filter_by(file_hash=rec.file_hash)
                .filter(err_filter)
                .count())
        if prev_imports > 0 and not added and not redo:
            secho("Already imported", fg='green', dim=True)
            return
        # It might get ugly here if we're trying to overwrite
        # old records but haven't deleted the appropriate
        # data_file_import models
        #if prev_imports > 0 and rec is not None:
        #    self.delete_session(rec)

        # Create a "data_file_import" object to track model-datafile links

        try:
            # import_datafile needs to return the top-level model(s)
            # created or modified during import.
            items = ensure_sequence(self.import_datafile(fn, rec, **kwargs))

            for created_model in items:
                # Track the import of the resulting models
                df_link = self.__track_model(rec, created_model)
                self.db.session.add(df_link)
                self.db.session.commit()
        except (SparrowImportError, NotImplementedError, IntegrityError) as err:
            self.db.session.rollback()
            df_link = self.__track_model(rec, None, error=str(err))
            if df_link is not None:
                self.db.session.add(df_link)
            secho(str(err), fg='red')

        if redo:
            self.__track_changes()
        # File records and trackers are added at the end,
        # outside of the try/except block, so they occur
        # regardness of error status
        self.db.session.commit()

    def __track_changes(self):
        new_changed = set(i for i in self.__new if self.__has_changes(i))
        modified = set(i for i in self.__dirty if self.__has_changes(i))

        def _echo(v, n, **kwargs):
            i = len(v)
            if i > 0:
                secho(f"{i} {n}", **kwargs)

        has_new_models = len(self.__new) > 0
        has_dirty_models = len(self.__dirty) > 0
        has_modified_models = len(modified) > 0

        if self.verbose:
            problems = (self.__new & new_changed) | (self.__dirty & modified)
            _echo(problems, "update attempted for unchanged model", fg='yellow')
            self.__print_changes(modified)

        if not has_modified_models:
            secho("No modifications", fg='green')
        else:
            _echo(self.__new, "records added", fg='green')
            _echo(modified, "records modified", fg='yellow')
        secho("")

    def __print_changes(self, dirty_records):
        pass

    def __has_changes(self, obj):
        for v in self.__object_changes(obj).values():
            if v.added is not None and  len(v.added) > 0:
                return True
            if v.deleted is not None and len(v.deleted) > 0:
                return True
        return False

    def __object_changes(self, obj):
        if not self.db.session.is_modified(obj):
            return {}
        return {k: v.history for k, v in inspect(obj).attrs.items()}

    def __track_model(self, rec, model=None, **kw):
        """
        Track the import of a given model from a data file
        """
        if model is None:
            return
        elif isinstance(model, self.m.session):
            kw['session_id'] = model.id
        elif isinstance(model, self.m.analysis):
            kw['analysis_id'] = model.id
        elif isinstance(model, self.m.sample):
            kw['sample_id'] = model.id
        else:
            raise NotImplementedError(
                "Only sessions, samples, and analyses "
                "can be tracked independently on import.")

        return self.db.get_or_create(
            self.m.data_file_link,
            file_hash=rec.file_hash,
            **kw)

    def iter_records(self, seq, **kwargs):
        """
        This is kind of outmoded by the new version of iterfiles
        """
        for rec in seq:
            secho(str(rec.file_path), dim=True)
            self.__import_datafile(None, rec, **kwargs)
