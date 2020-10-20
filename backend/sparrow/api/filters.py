from webargs.fields import DelimitedList, Str, Int, Boolean
from .exceptions import ValidationError


def _schema_fields(schema):
    return {getattr(f, "data_key", k): f for k, f in schema.fields.items()}


class BaseFilter:
    params = None
    help = None

    def __init__(self, model, schema=None):
        self.model = model
        self.schema = schema

    def should_apply(self):
        return True

    def apply(self, query, args):
        return query

    def __call__(self, query, args):
        if not self.should_apply():
            return query
        return self.apply(args, query)


class AuthorityFilter(BaseFilter):
    params = dict(authority=Str(missing=None))
    help = dict(authority="Authority")

    def should_apply(self):
        return hasattr(self.model, "authority")

    def apply(self, args, query):
        if args["authority"] is None:
            return query
        return query.filter(self.model.authority == args["authority"])


class FieldExistsFilter(BaseFilter):
    key = "has"

    @property
    def params(self):
        return {
            self.key: DelimitedList(
                Str(), missing=[], description="filter by [field] existence"
            )
        }

    def should_apply(self):
        """This only works with objects defined with a schema for now"""
        return self.schema is not None

    def _field_filter(self, field):
        orm_attr = getattr(self.model, field.name)
        if hasattr(field, "related_model"):
            if orm_attr.property.uselist:
                return orm_attr.any()
            else:
                return orm_attr.has()
        return orm_attr.isnot(None)

    def apply(self, args, query):
        fields = _schema_fields(self.schema())
        # Filter by has
        for has_field in args[self.key]:
            try:
                field = fields[has_field]
            except KeyError:
                raise ValidationError(f"'{has_field}' is not a valid field")
            query = query.filter(self._field_filter(field))
        return query


class FieldNotExistsFilter(FieldExistsFilter):
    key = "not_has"

    def _field_filter(self, field):
        orm_attr = getattr(self.model, field.name)
        if hasattr(field, "related_model"):
            if orm_attr.property.uselist:
                return ~orm_attr.any()
            else:
                return ~orm_attr.has()
        return orm_attr.is_(None)
