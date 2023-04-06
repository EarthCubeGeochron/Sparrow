from .util import coalesce_nan


class ImperativeImportHelperMixin:
    """This class holds helpers for imperative import helpers that have been
    made redundant by the schema-based importers that were introduced in Sparrow v1.5.
    These tools will be deprecated and may be removed from the codebase sometime after
    the Sparrow v2.0 milestone."""

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
            self.m.publication, doi=doi, defaults=dict(title=title)
        )

    def project(self, name):
        return self.db.get_or_create(self.m.project, name=name)

    def researcher(self, **kwargs):
        return self.db.get_or_create(self.m.researcher, **kwargs)

    ## Vocabulary

    def unit(self, id, description=None):
        u = self.db.get_or_create(
            self.m.vocabulary_unit, id=id, defaults=dict(authority=self.authority)
        )
        if u is not None:
            u.description = description
        return u

    def error_metric(self, id, description=None):
        if not id:
            return None
        em = self.db.get_or_create(
            self.m.vocabulary_error_metric,
            id=id,
            defaults=dict(authority=self.authority),
        )
        if description is not None:
            em.description = description
        return em

    def parameter(self, id, description=None):
        p = self.db.get_or_create(
            self.m.vocabulary_parameter, id=id, defaults=dict(authority=self.authority)
        )
        if description is not None:
            p.description = description
        return p

    def method(self, id):
        return self.db.get_or_create(
            self.m.vocabulary_method, id=id, defaults=dict(authority=self.authority)
        )

    def material(self, id, type_of=None):
        if id is None:
            return None
        m = self.db.get_or_create(
            self.m.vocabulary_material, id=id, defaults=dict(authority=self.authority)
        )
        if type_of is not None:
            m._material = self.material(type_of)
        return m

    def analysis_type(self, id, type_of=None):
        m = self.db.get_or_create(
            self.m.vocabulary_analysis_type,
            id=id,
            defaults=dict(authority=self.authority),
        )
        if type_of is not None:
            m._analysis_type = self.analysis_type(type_of)
        return m

    def datum_type(self, parameter, unit="unknown", error_metric=None, **kwargs):
        error_metric = self.error_metric(error_metric)
        try:
            error_metric_id = error_metric.id
        except AttributeError:
            error_metric_id = None

        unit = self.unit(unit)

        # Error values are *assumed* to be at the 1s level, apparently
        parameter = self.parameter(parameter)

        dt = self.db.get_or_create(
            self.m.datum_type,
            parameter=parameter.id,
            error_metric=error_metric_id,
            unit=unit.id,
            **kwargs,
        )
        return dt

    def analysis(self, type=None, **kwargs):
        if type is not None:
            type = self.analysis_type(type).id
        m = self.db.get_or_create(self.m.analysis, analysis_type=type, **kwargs)
        return m

    def add_analysis(self, session, type=None, **kwargs):
        """Deprecated"""
        return self.analysis(session_id=session.id, type=type, **kwargs)

    def attribute(self, analysis, parameter, value):
        if value is None:
            return None
        self.db.session.flush()
        param = self.parameter(parameter)
        attr = self.db.get_or_create(self.m.attribute, parameter=param.id, value=value)
        analysis.attribute_collection.append(attr)
        return attr

    def datum(self, analysis, parameter, value, error=None, **kwargs):
        value = coalesce_nan(value)
        if value is None:
            return None
        type = self.datum_type(parameter, **kwargs)
        self.db.session.flush()
        datum = self.db.get_or_create(self.m.datum, analysis=analysis.id, type=type.id)
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
        const = self.db.get_or_create(
            self.m.constant, value=value, error=error, type=type.id
        )
        analysis.constant_collection.append(const)
        self.db.session.flush()
        return const
