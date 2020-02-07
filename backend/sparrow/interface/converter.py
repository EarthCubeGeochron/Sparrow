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
    'datum': ['datum_type'],
    'datum_type': []
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

        if len(prop.local_columns) == 1:
            current_col = list(prop.local_columns)[0].name
            # Self-referential foreign keys should have
            # the relationship named after the column
            if prop.target == prop.parent.mapped_table:
                return current_col
            # One-to-many models should have the field
            # named after the local column
            if prop.secondary is None and not prop.uselist:
                return current_col
        # Otherwise, we go with the name of the remote model.
        return prop.target.name

    def fields_for_model(
        self,
        model,
        *,
        include_fk=False,
        fields=None,
        exclude=None,
        base_fields=None,
        dict_cls=dict
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

    def _should_exclude_field(prop, **kwargs):
        pass

    def _get_field_kwargs_for_property(self, prop):
        kwargs = super()._get_field_kwargs_for_property(prop)
        print(prop.columns[0].name)
        if hasattr(prop, "direction"): # Relationship property
            print(prop, kwargs)
            return kwargs

        for col in prop.columns:
            is_integer = isinstance(col.type, Integer)
            if col.name == 'audit_id' and is_integer:
                kwargs['dump_only'] = True
                return kwargs

            if is_integer and col.primary_key:
                # Integer primary keys should be dump-only, probably
                # We could probably check for a default sequence
                # if we wanted to be general...
                kwargs['dump_only'] = True
            elif not col.nullable:
                kwargs['required'] = True

            if isinstance(col.type, UUID):
                kwargs['dump_only'] = True
                kwargs['required'] = False

            dump_only = kwargs.get('dump_only', False)
            if not dump_only and not col.nullable:
                kwargs['required'] = True
            if dump_only:
                kwargs['required'] = False
        return kwargs

    def property2field(self, prop, **kwargs):
        if not isinstance(prop, RelationshipProperty):
            return super().property2field(prop, **kwargs)

        # Exclude field based on table name
        this_table = prop.parent.mapped_table
        other_table = prop.target.name

        if prop.target == this_table and prop.uselist:
            # Don't allow self-referential collections
            return None

        # Don't allow the 'many' side of some 'one-to-many'
        # relationships nest their parents...
        r = prop.mapper.relationships
        many_to_one = not prop.uselist and r[prop.backref[0]].uselist
        remotes = allowed_collections.get(this_table.name, [])

        if many_to_one and other_table not in remotes:
            return None

        # Exclude foreign key columns from nesting
        exclude = []
        # Get the class for this relationship
        #name = self._name_for_relationship_property(prop)

        #print(len(prop.local_columns))
        #print(name, prop)
        #    name = col.name

        # The "name" is actually the name of the related model, NOT the name
        # of field
        cls = prop.mapper.class_
        name = to_schema_name(cls.__name__)

        return Nested(name, many=prop.uselist, exclude=exclude, **kwargs)
