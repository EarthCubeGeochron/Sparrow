
class BaseImporter(object):
    """
    A basic Sparrow importer for Geochron.org XML
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
            id=id, authority=self.authority)

    def error_metric(self, id):
        if not id: return None
        return self.db.get_or_create(
            self.models.error_metric,
            id=id, authority=self.authority)

    def parameter(self, id):
        return self.db.get_or_create(
            self.models.parameter,
            id=id, authority=self.authority)

    def method(self, id):
        return self.db.get_or_create(
            self.models.method,
            id=id, authority=self.authority)

    def material(self, id):
        return self.db.get_or_create(
            self.models.material,
            id=id, authority=self.authority)

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
