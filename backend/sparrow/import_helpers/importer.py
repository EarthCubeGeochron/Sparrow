from click import secho
from ..util import relative_path
from sqlalchemy import text

class SparrowImportError(Exception):
    pass

class BaseImporter(object):
    """
    A basic Sparrow importer to be subclassed.
    """
    authority = None
    def __init__(self, db):
        self.db = db
        self.models = self.db.mapped_classes

    def sample(self, **kwargs):
        return self.db.get_or_create(self.models.sample, **kwargs)

    def location(self, lon, lat):
        return f"SRID=4326;POINT({lon} {lat})"

    def publication(self, doi, title=None):
        return self.db.get_or_create(
            self.models.publication,
            doi=doi, defaults=dict(title=title))

    def unit(self, id):
        return self.db.get_or_create(
            self.models.unit,
            id=id, defaults=dict(authority=self.authority))

    def error_metric(self, id):
        if not id: return None
        return self.db.get_or_create(
            self.models.error_metric,
            id=id, defaults=dict(authority=self.authority))

    def parameter(self, id):
        return self.db.get_or_create(
            self.models.parameter,
            id=id, defaults=dict(authority=self.authority))

    def method(self, id):
        return self.db.get_or_create(
            self.models.method,
            id=id, defaults=dict(authority=self.authority))

    def material(self, id):
        return self.db.get_or_create(
            self.models.material,
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
            self.models.datum_type,
            parameter=parameter.id,
            error_metric=error_metric_id,
            unit=unit.id,
            **kwargs)
        return dt

    def datum(self, parameter, value, error=None, **kwargs):
            type = self.datum_type(parameter, **kwargs)
            datum = self.models.datum(
                value=value,
                error=error)
            datum._datum_type=type
            return datum

    def import_datafile(self, rec):
        raise NotImplementedError()

    def delete_session(self, rec):
        """
        Delete session(s) given a data file model
        """
        fn = relative_path(__file__, 'sql', 'delete-session.sql')
        sql = text(open(fn).read())
        self.db.session.execute(sql, {'file_hash': rec.file_hash})
        self.db.session.commit()

    def iterfiles(self, file_sequence, **kwargs):
        kwargs['parse_filename'] = lambda f: str(f)
        self.iteritems(file_sequence, **kwargs)

    def iteritems(self, seq, **kwargs):
        fn = kwargs.pop("parse_filename", lambda f: str(f.file_path))
        stop_on_error = kwargs.pop("stop_on_error", False)
        for f in seq:
            try:
                secho(fn(f), dim=True)
                imported = self.import_datafile(f)
                self.db.session.commit()
                if not imported:
                    secho("Already imported", fg='green', dim=True)
            except (SparrowImportError, NotImplementedError) as e:
                if stop_on_error: raise e
                self.db.session.rollback()
                secho(str(e), fg='red')
