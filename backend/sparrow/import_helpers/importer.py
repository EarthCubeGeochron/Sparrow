from click import secho
from sqlalchemy import text
from datetime import datetime
from pathlib import Path
from os import environ
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from .util import md5hash, SparrowImportError, ensure_sequence
from ..util import relative_path, pretty_print

class BaseImporter(object):
    """
    A basic Sparrow importer to be subclassed.
    """
    authority = None
    def __init__(self, db, **kwargs):
        self.db = db
        self.m = self.db.model
        print_sql = kwargs.pop("print_sql", False)

        # This is kinda unsatisfying
        self.basedir = environ.get("SPARROW_DATA_DIR", None)

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

        # Deprecated
        self.models = self.m

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

    def unit(self, id):
        return self.db.get_or_create(
            self.m.vocabulary_unit,
            id=id, defaults=dict(authority=self.authority))

    def error_metric(self, id):
        if not id: return None
        return self.db.get_or_create(
            self.m.vocabulary_error_metric,
            id=id, defaults=dict(authority=self.authority))

    def parameter(self, id):
        return self.db.get_or_create(
            self.m.vocabulary_parameter,
            id=id, defaults=dict(authority=self.authority))

    def method(self, id):
        return self.db.get_or_create(
            self.m.vocabulary_method,
            id=id, defaults=dict(authority=self.authority))

    def material(self, id, type_of=None):
        m = self.db.get_or_create(
            self.m.vocabulary_material,
            id=id, defaults=dict(authority=self.authority))
        if type_of is not None:
            m._material = self.material(type_of)
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

    def add_analysis(self, session, **kwargs):
        return self.db.get_or_create(
            self.m.analysis,
            session_id=session.id,
            **kwargs
        )

    def datum(self, analysis, parameter, value, error=None, **kwargs):
        type = self.datum_type(parameter, **kwargs)
        datum = self.db.get_or_create(self.m.datum,
            type=type.id, analysis=analysis.id)
        datum.value = value
        datum.error = error

        return datum

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

    def __set_file_info(self, fn, rec):
        infile = Path(fn)
        _ = infile.stat().st_mtime
        mtime = datetime.utcfromtimestamp(_)

        if self.basedir is not None:
            infile = infile.relative_to(self.basedir)

        rec.file_mtime = mtime
        rec.basename = infile.name
        rec.file_path = str(infile)

    def __create_data_file_record(self, fn):

        # Get file mtime and hash
        hash = md5hash(str(fn))

        # Get data file record if it exists
        rec = self.db.get(self.m.data_file, hash)
        added = rec is None
        if added:
            rec = self.m.data_file(file_hash=hash)
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
                self.__track_model(rec, created_model)
                self.db.session.flush()
        except (SparrowImportError, NotImplementedError, IntegrityError) as err:
            self.db.session.rollback()
            self.__track_model(rec, None, error=str(err))
            secho(str(err)+"\n", fg='red')

        if redo:
            dirty = set(i for i in set(self.__dirty) if self.db.session.is_modified(i))
            dirty = list(dirty | self.__new)
            if len(dirty) == 0:
                secho("No modifications", fg='green')
            else:
                secho(f"{len(dirty)} records modified")

        # File records and trackers are added at the end,
        # outside of the try/except block, so they occur
        # regardness of error status
        self.db.session.commit()

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
