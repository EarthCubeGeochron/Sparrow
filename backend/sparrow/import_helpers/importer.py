from click import secho
from sqlalchemy import text
from datetime import datetime
from pathlib import Path
from os import environ
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
from IPython import embed

from .util import md5hash, SparrowImportError, ensure_sequence
from ..util import relative_path
from .imperative_helpers import ImperativeImportHelperMixin


class BaseImporter(ImperativeImportHelperMixin):
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

        # This is kinda unsatisfying
        self.basedir = environ.get("SPARROW_DATA_DIR", None)

        # Allow us to turn of change-tracking for speed
        self.__dirty = set()
        self.__new = set()
        self.__deleted = set()

        @event.listens_for(self.db.session, "before_flush")
        def on_before_flush(session, flush_context, instances):
            self.__dirty |= set(session.dirty)
            self.__new |= set(session.new)
            self.__deleted |= set(session.deleted)

        @event.listens_for(self.db.session, "after_commit")
        def on_after_commit(session):
            self.__dirty = set()
            self.__new = set()
            self.__deleted = set()

        if print_sql:

            @event.listens_for(self.db.engine, "after_cursor_execute", named=True)
            def receive_after_cursor_execute(**kw):
                statement = kw.pop("statement")
                if statement.startswith("SELECT"):
                    return
                secho(str(statement).strip())

        if self.file_type is not None:
            v = self.db.get_or_create(self.m.data_file_type, id=self.file_type)
            self.add(v)
            self.db.session.commit()

        # Deprecated
        self.models = self.m

    def session_changes(self):
        def changed(i):
            return self.db.session.is_modified(i, include_collections=True)

        # Bug: For some reason, changes on many-to-many links are not recorded.
        return dict(
            dirty=self.__dirty,
            modified=set(i for i in set(self.__dirty) if changed(i)),
            new=self.__new,
            deleted=self.__deleted,
        )

    ###
    # Data file importing
    ###

    def warn(self, message):
        secho(str(message), fg="yellow")

    def import_datafile(self, fn, rec, **kwargs):
        """An importer must `yield` models that are to be tracked in the `data_file_link` table."""
        raise NotImplementedError()

    def delete_session(self, rec):
        """
        Delete session(s) and associated analysis and datum records,
        given a data file model
        """
        fn = relative_path(__file__, "sql", "delete-session.sql")
        sql = text(open(fn).read())
        self.db.session.execute(sql, {"file_hash": rec.file_hash})

    def iterfiles(self, file_sequence, **kwargs):
        """
        This file iterator tracks files in the *data_file* table,
        checks if they have been imported, and potentially imports
        if needed.
        """
        for fn in file_sequence:
            self.__import_datafile(fn, None, **kwargs)

    def iter_records(self, seq, **kwargs):
        """
        This is kind of outmoded by the new version of iterfiles
        """
        for rec in seq:
            if rec is None:
                continue
            secho(str(rec.file_path), dim=True)
            self.__import_datafile(None, rec, **kwargs)

    def __set_file_info(self, infile, rec):
        _ = infile.stat().st_mtime
        mtime = datetime.utcfromtimestamp(_)
        rec.file_mtime = mtime
        rec.basename = infile.name

    def _find_existing_data_file(self, file_path=None, file_hash=None):
        # Get data file record if it exists
        ## TODO: First, get file with same hash (i.e., exact same file contents), attempting to relink if non-existant
        return (
            self.db.session.query(self.m.data_file)
            .filter_by(file_path=file_path)
            .first()
        )

    def _create_data_file_record(self, fn):

        # Get the path location (this must be unique)
        _infile = Path(fn)
        if self.basedir is not None:
            infile = _infile.relative_to(self.basedir)
        file_path = str(infile)

        # Get file hash
        hash = md5hash(str(fn))

        rec = self._find_existing_data_file(file_path=file_path, file_hash=hash)

        should_add_record = rec is None
        if should_add_record:
            rec = self.m.data_file(file_path=file_path, file_hash=hash)

        updated = rec.file_hash != hash
        if updated:
            rec.file_hash = hash

        rec.file_type = self.file_type

        self.db.session.add(rec)

        self.__set_file_info(_infile, rec)
        return rec, should_add_record

    def __import_datafile(self, fn, rec=None, **kwargs):
        """
        A wrapper for data file import that tracks data files through
        the import process and builds links to data file types.

        :param fix_errors  Fix errors that have previously been ignored
        """
        secho(str(fn), dim=True)
        redo = kwargs.pop("redo", False)
        added = False
        if rec is None:
            rec, added = self._create_data_file_record(fn)

        err_filter = True
        m = self.m.data_file_link
        if kwargs.pop("fix_errors", False):
            err_filter = m.error.is_(None)
        prev_imports = (
            self.db.session.query(m)
            .filter_by(file_hash=rec.file_hash)
            .filter(err_filter)
            .count()
        )
        if prev_imports > 0 and not added and not redo:
            secho("Already imported", fg="green", dim=True)
            return
        # It might get ugly here if we're trying to overwrite
        # old records but haven't deleted the appropriate
        # data_file_import models
        # if prev_imports > 0 and rec is not None:
        #    self.delete_session(rec)

        # Create a "data_file_import" object to track model-datafile links

        try:
            # import_datafile needs to return the top-level model(s)
            # created or modified during import.
            items = ensure_sequence(self.import_datafile(fn, rec, **kwargs))

            for created_model in items:
                if created_model is None:
                    continue
                # Track the import of the resulting models
                df_link = self.__track_model(rec, created_model)
                if df_link is not None:
                    self.db.session.add(df_link)
                self.db.session.commit()
        except (SparrowImportError, NotImplementedError, IntegrityError) as err:
            self.db.session.rollback()
            df_link = self.__track_model(rec, None, error=str(err))
            if df_link is not None:
                self.db.session.add(df_link)
            self.db.session.commit()
            secho(str(err), fg="red")

        if redo:
            self.__track_changes()
        # File records and trackers are added at the end,
        # outside of the try/except block, so they occur
        # regardness of error status
        self.db.session.commit()
        secho("")

    def __track_changes(self):
        new_changed = set(i for i in self.__new if self.__has_changes(i))
        modified = set(i for i in self.__dirty if self.__has_changes(i))

        def _echo(v, n, **kwargs):
            i = len(v)
            if i > 0:
                secho(f"{i} {n}", **kwargs)

        # has_new_models = len(self.__new) > 0
        # has_dirty_models = len(self.__dirty) > 0
        has_modified_models = len(modified) > 0

        if self.verbose:
            problems = (self.__new & new_changed) | (self.__dirty & modified)
            _echo(problems, "update attempted for unchanged model", fg="yellow")
            self.__print_changes(modified)

        if not has_modified_models:
            secho("No modifications", fg="green")
        else:
            _echo(self.__new, "records added", fg="green")
            _echo(modified, "records modified", fg="yellow")
        secho("")

    def __print_changes(self, dirty_records):
        pass

    def __has_changes(self, obj):
        for v in self.__object_changes(obj).values():
            if v.added is not None and len(v.added) > 0:
                return True
            if v.deleted is not None and len(v.deleted) > 0:
                return True
        return False

    def __object_changes(self, obj):
        if not self.db.session.is_modified(obj):
            return {}
        return {k: v.history for k, v in inspect(obj).attrs.items()}

    def __track_model(self, rec, model=None, **defaults):
        """
        Track the import of a given model from a data file
        """
        params = dict(_data_file=rec, defaults=defaults)
        print(model, params)
        if isinstance(model, self.m.session):
            params["_session"] = model
        elif isinstance(model, self.m.analysis):
            params["_analysis"] = model
        elif isinstance(model, self.m.sample):
            params["_sample"] = model
        elif "error" not in defaults:
            raise NotImplementedError(
                "Only sessions, samples, and analyses "
                "can be tracked independently on import."
            )

        return self.db.get_or_create(self.m.data_file_link, **params)


class CloudImporter(BaseImporter):
    """
    Importer to be subclassed that is geared towards S3 and compatible
    cloud storage systems.
    """

    pass
