from marshmallow_sqlalchemy import ModelConverter
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested

from geoalchemy2 import Geography, Geometry
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.types import Integer
from sqlalchemy.dialects.postgresql import UUID
from stringcase import pascalcase

from ..database.mapper.util import trim_postfix
from .fields import GeometryField, EnumField


def to_schema_name(name):
    return pascalcase(name+"_schema")


# Control how relationships can be resolved
allowed_collections = {
    'sample': ['session'],
    'session': 'all',
    'analysis': ['datum', 'attribute', 'constant', 'analysis_type'],
    'attribute': ['parameter', 'unit'],
    'project': ['researcher', 'publication', 'session'],
    'datum': ['datum_type'],
    'datum_type': [
        'parameter',
        'unit',
        'error_unit',
        'error_metric'
    ]
}


def allow_nest(outer, inner):
    if outer == inner:
        # Tables can always nest themselves
        return True
    coll = allowed_collections.get(outer, [])
    if coll == 'all':
        return True
    return inner in coll


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

    def _key_for_property(self, prop):
        if not isinstance(prop, RelationshipProperty):
            return prop.key

        # # Normal column
        # if hasattr(prop, 'columns') and len(prop.columns) == 1:
        #     return trim_postfix(prop.columns[0].name, "_id")

        # Relationship with local columns
        if hasattr(prop, 'local_columns') and len(prop.local_columns) == 1:
            col_name = list(prop.local_columns)[0].name
            if col_name != 'id':
                return trim_postfix(col_name, "_id")

        #if prop.key.endswith('_id'):
        #    return prop.target.name

        # Self-referential foreign keys should have
        # the relationship named after the column
        if prop.key == prop.parent.mapped_table:
            return prop.key
        # One-to-many models should have the field
        # named after the local column
        if prop.secondary is None and not prop.uselist:
            return prop.key
        # Otherwise, we go with the name of the remote model.
        return prop.target.name

    def fields_for_model(self, model, **kwargs):
        # Shim fields_for_model so we can control the generated property names
        # Precompute new keys so we can use properties
        new_keys = {prop.key: self._key_for_property(prop)
                    for prop in model.__mapper__.iterate_properties}
        # Convert fields to models using library code.
        fields = super().fields_for_model(model, **kwargs)
        return {new_keys[k]: v for k, v in fields.items() if v is not None}

    def _should_exclude_field(self, prop, fields=None, exclude=None):
        if fields and prop.key not in fields:
            return True
        if exclude and prop.key in fields:
            return True

        if not isinstance(prop, RelationshipProperty):
            return False

        # ## Deal with relationships here #

        if prop.target.name == 'data_file_link':
            # Data files are currently exclusively dealt with internally...
            # (this may change)
            return True

        # # Exclude field based on table name
        this_table = prop.parent.tables[0]
        other_table = prop.target

        if prop.target == this_table and prop.uselist:
            # Don't allow self-referential collections
            return True

        if prop.uselist and not allow_nest(this_table.name, prop.target.name):
            # Disallow list fields that aren't related (these usually don't have
            # corresponding local columns)
            return True

        return False

    def _get_field_kwargs_for_property(self, prop):
        kwargs = super()._get_field_kwargs_for_property(prop)

        if isinstance(prop, RelationshipProperty): # Relationship property
            cols = list(getattr(prop, 'local_columns', []))
            kwargs['required'] = False
            for col in cols:
                if not col.nullable:
                    kwargs['required'] = True
            if prop.uselist:
                kwargs['required'] = False

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

        # The "name" is actually the name of the related model, NOT the name
        # of field
        cls = prop.mapper.class_
        name = to_schema_name(cls.__name__)

        field_kwargs = self._get_field_kwargs_for_property(prop)
        field_kwargs.update(**kwargs)

        this_table = prop.parent.tables[0]
        if not allow_nest(this_table.name, prop.target.name):
            # Fields that are not allowed to be nested
            return Related(name, **field_kwargs)
        if prop.target.schema == 'enum':
            # special carve-out for enums represented as foreign keys
            # (these should be stored in the 'enum' schema):
            return EnumField(name, **field_kwargs)

        # # TODO: remove parent fields
        exclude = []
        r = prop.mapper.relationships
        if prop.backref is not None:
            remote_prop = r[prop.backref[0]]
            remote_field = self._key_for_property(remote_prop)
            if not self._should_exclude_field(remote_prop):
                exclude.append(remote_field)

        return Nested(name, many=prop.uselist, exclude=exclude, **field_kwargs)
