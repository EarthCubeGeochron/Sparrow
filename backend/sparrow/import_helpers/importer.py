from click import secho
from sqlalchemy import text
from datetime import datetime
from pathlib import Path
from os import environ

from .util import md5hash, SparrowImportError, ensure_sequence
from ..util import relative_path

class BaseImporter(object):
    """
    A basic Sparrow importer to be subclassed.
    """
    authority = None
    def __init__(self, db):
        self.db = db
        self.m = self.db.model

        # This is kinda unsatisfying
        self.basedir = environ.get("SPARROW_DATA_DIR", None)

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

    def unit(self, id):
        return self.db.get_or_create(
            self.m.unit,
            id=id, defaults=dict(authority=self.authority))

    def error_metric(self, id):
        if not id: return None
        return self.db.get_or_create(
            self.m.error_metric,
            id=id, defaults=dict(authority=self.authority))

    def parameter(self, id):
        return self.db.get_or_create(
            self.m.parameter,
            id=id, defaults=dict(authority=self.authority))

    def method(self, id):
        return self.db.get_or_create(
            self.m.method,
            id=id, defaults=dict(authority=self.authority))

    def material(self, id):
        return self.db.get_or_create(
            self.m.material,
            id=id, defaults=dict(authority=self.authority))

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

    def datum(self, parameter, value, error=None, **kwargs):
            type = self.datum_type(parameter, **kwargs)
            datum = self.m.datum(
                value=value,
                error=error)
            datum._datum_type=type
            return datum

    ###
    # Data file importing
    ###

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
        redo = kwargs.pop("redo", False)

        for fn in file_sequence:
            secho(str(fn), dim=True)
            self.__import_datafile(fn)

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

        prev_imports = (
            self.db.session
                .query(self.m.data_file_link)
                .filter_by(file_hash=rec.file_hash)
                .count())
        if prev_imports > 0 and not added and not redo:
            secho("Already imported", fg='green', dim=True)
            return
        # It might get ugly here if we're trying to overwrite
        # old records but haven't deleted the appropriate
        # data_file_import models

        # Create a "data_file_import" object to track model-datafile links
        im = self.m.data_file_link()
        im._data_file = rec

        try:
            # import_datafile needs to return the top-level model(s)
            # created or modified during import.
            items = ensure_sequence(self.import_datafile(fn, rec, **kwargs))

            for created_model in items:
                self.db.session.add(created_model)
                # Track the import of the resulting models
                self.__track_model(im, created_model)
        except (SparrowImportError, NotImplementedError) as err:
            self.db.session.rollback()
            error = str(err)
            im.error = error
            secho(error, fg='red')

        # File records and trackers are added at the end,
        # outside of the try/except block so they occur
        # regardness of error status
        self.db.session.add(rec)
        self.db.session.add(im)
        self.db.session.commit()

    def __track_model(self, im, model):
        """
        Track the import of a given model from a data file
        """
        if isinstance(model, self.m.session):
            im._session = model
        elif isinstance(model, self.m.analysis):
            im._analysis = model
        elif isinstance(model, self.m.sample):
            im._sample = model
        else:
            raise NotImplementedError(
                "Only sessions, samples, and analyses "
                "can be tracked independently on import.")

    def iter_records(self, seq, **kwargs):
        """
        This is kind of outmoded by the new version of iterfiles
        """
        for rec in seq:
            secho(str(rec.file_path), dim=True)
            self.__import_datafile(None, rec, **kwargs)
