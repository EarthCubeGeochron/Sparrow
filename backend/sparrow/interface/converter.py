from marshmallow_sqlalchemy import ModelConverter
from marshmallow.fields import Nested

from geoalchemy2 import Geography, Geometry
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.types import Integer
from sqlalchemy.dialects.postgresql import UUID
from stringcase import pascalcase

from .geometry import GeometryField


def to_schema_name(name):
    return pascalcase(name+"_schema")

# Control how relationships can be resolved
allowed_collections = {
    'sample': ['session'],
    'session': ['analysis', 'attribute'],
    'analysis': ['datum', 'attribute'],
    'project': ['researcher', 'publication', 'session'],
}


class SmartNested(Nested):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    def serialize(self, attr, obj, accessor=None):
        #if attr not in obj.__dict__:
        #    return {"id": int(getattr(obj, attr + "_id"))}
        return super().serialize(attr, obj, accessor)


class SparrowConverter(ModelConverter):
    # Make sure that we can properly convert geometries
    # and geographies
    SQLA_TYPE_MAPPING = dict(
        list(ModelConverter.SQLA_TYPE_MAPPING.items())
        + list({
            Geometry: GeometryField,
            Geography: GeometryField
            }.items()
        ))

    def _key_for_field(self, prop):
        if not isinstance(prop, RelationshipProperty):
            return prop.key

        tbl = prop.parent.mapped_table
        if prop.target == tbl:
            return list(prop.local_columns)[0].name
        return prop.target.name

    def fields_for_model(
        self,
        model,
        *,
        include_fk=False,
        fields=None,
        exclude=None,
        base_fields=None,
        dict_cls=dict,
    ):
        result = dict()
        base_fields = base_fields or {}
        for prop in model.__mapper__.iterate_properties:
            key = self._key_for_field(prop)
            if self._should_exclude_field(prop, fields=fields, exclude=exclude):
                # Allow marshmallow to validate and exclude the field key.
                result[key] = None
                continue
            if hasattr(prop, "columns"):
                if not include_fk:
                    # Only skip a column if there is no overriden column
                    # which does not have a Foreign Key.
                    for column in prop.columns:
                        if not column.foreign_keys:
                            break
                    else:
                        continue
            field = base_fields.get(prop.key) or self.property2field(prop)
            if field:
                result[key] = field
        return result

    def _get_field_kwargs_for_property(self, prop):
        kwargs = super()._get_field_kwargs_for_property(prop)

        for col in prop.columns:
            if isinstance(col.type, Integer) and col.primary_key:
                # Integer primary keys should be dump-only, probably
                kwargs['dump_only'] = True
            if isinstance(col.type, UUID):
                kwargs['dump_only'] = True
        return kwargs

    def property2field(self, prop, **kwargs):
        if not isinstance(prop, RelationshipProperty):
            return super().property2field(prop, **kwargs)

        # Get the class for this relationship
        cls = prop.mapper.class_
        name = to_schema_name(cls.__name__)
        # Exclude field based on table name
        if prop.target.name == 'data_file_link':
            return None

        this_table = prop.parent.mapped_table

        if prop.target == this_table and prop.uselist:
            # Don't allow self-referential collections
            return None

        coll = allowed_collections.get(this_table.name, [])
        if prop.uselist and prop.target.name not in coll:
            # Only certain collections are allowed
            return None

        # Exclude foreign key columns from nesting
        exclude = []
        # Exclude all back-references to models already defined
        if prop.backref is not None:
            pass

        #prop.key = prop.target.name

        #col = list(prop.local_columns)[0]
        #if not col.primary_key:
        #    name = col.name

        return Nested(name, many=prop.uselist, exclude=exclude)
