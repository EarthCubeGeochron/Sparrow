from marshmallow_sqlalchemy import ModelConverter

# We need to use marshmallow_sqlalchemy's own implementation
# of the 'Nested' field in order to pass along the SQLAlchemy session
# to nested schemas.
# See https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/67
from marshmallow_sqlalchemy.fields import Related, RelatedList

import geoalchemy2 as geo
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.types import Integer, Numeric, DateTime
from sqlalchemy.dialects import postgresql
from macrostrat.utils import get_logger

from macrostrat.database.mapper.utils import trim_postfix
from .fields import (
    Geometry,
    Enum,
    JSON,
    SmartNested,
    UUID,
    DateTimeExt,
    PassThroughRelated,
)
from .util import to_schema_name


log = get_logger(__name__)

# Control how relationships can be resolved for import and serialization
# TODO:
# - we might want to slightly decouple the import and representation sides of this
# - we also might want to move this to a configuration section so it can be modified
allowed_collections = {
    "data_file": ["data_file_link"],
    "data_file_link": ["session", "sample", "analysis", "instrument_session"],
    "sample": [
        "session",
        "material",
        "project",
        "sample_geo_entity",
        "researcher",
        "publication",
        "tag",
        "attribute",
    ],
    "geo_entity": "all",
    "sample_geo_entity": "all",
    "session": [
        "analysis",
        "attribute",
        "project",
        "publication",
        "sample",
        "instrument",
        "instrument_session",
        "target",
        "method",
        "tag",
    ],
    "analysis": ["datum", "attribute", "constant", "analysis_type", "material", "tag"],
    "attribute": ["parameter", "unit"],
    "instrument_session": ["session", "project", "researcher"],
    "project": [
        "researcher",
        "publication",
        "session",
        "sample",
        "instrument_session",
        "tag",
    ],
    "datum": ["datum_type", "tag"],
    "datum_type": ["parameter", "unit", "error_unit", "error_metric"],
}

# This field exclusion only makes sense for LaserChron right now
exclude_fields = {"data_file": ["csv_data"]}


def allow_nest(outer, inner):
    if outer == inner:
        # Tables can always nest themselves
        return True
    coll = allowed_collections.get(outer, [])
    if coll == "all":
        return True
    return inner in coll


class SparrowConverter(ModelConverter):
    # Make sure that we can properly convert geometries
    # and geographies
    SQLA_TYPE_MAPPING = dict(
        list(ModelConverter.SQLA_TYPE_MAPPING.items())
        + list(
            {
                geo.Geometry: Geometry,
                geo.Geography: Geometry,
                postgresql.JSON: JSON,
                postgresql.JSONB: JSON,
                postgresql.UUID: UUID,
                DateTime: DateTimeExt,
            }.items()
        )
    )

    def _get_key(self, prop):
        # Only change columns for relationship properties
        if not isinstance(prop, RelationshipProperty):
            return prop.key

        # Relationship with a single local column should be named for its
        # column (less '_id' postfix)
        if hasattr(prop, "local_columns") and len(prop.local_columns) == 1:
            col_name = list(prop.local_columns)[0].name
            # Special case for 'data_file_link'
            if col_name == "file_hash":
                return prop.target.name
            if col_name != "id":
                return trim_postfix(col_name, "_id")

        # One-to-many models should have the field
        # named after the local column
        if prop.secondary is None and not prop.uselist:
            return prop.key

        # For tables not in Sparrow's standard schemas, we make sure to append the
        # schema name in front of keys, in order for views etc. to not trample
        # on already-used names. This was added in order to solve problems
        # with the automapping of `core_view.datum`.
        #
        # It may be desirable to improve this by adding a __prefix before views,
        # OR by making _ALL_ non-public schema tables require a prefix.
        if prop.target.schema not in [None, "vocabulary", "enum"]:
            return f"{prop.target.schema}_{prop.target.name}"

        # Otherwise, we go with the name of the target model.
        return str(prop.target.name)

    def fields_for_model(self, model, **kwargs):
        fields = super().fields_for_model(model, **kwargs)
        return {k: v for k, v in fields.items() if v is not None}

    def _should_exclude_field(self, prop, fields=None, exclude=None):
        if fields and prop.key not in fields:
            return True
        if exclude and prop.key in fields:
            return True

        # Get the name of this table
        this_table = prop.parent.tables[0]

        # Exclude fields referenced in our `exclude_fields` dict
        if prop.key in exclude_fields.get(this_table.name, []):
            return True

        if not isinstance(prop, RelationshipProperty):
            return False

        # ## Deal with relationships here #

        # if prop.target.name == "data_file_link":
        #     # Data files are currently exclusively dealt with internally...
        #     # (this may change)
        #     return True

        # # Exclude field based on table name
        other_table = prop.target

        if other_table == this_table and prop.uselist:
            # Don't allow self-referential collections
            return True

        if prop.uselist and not allow_nest(this_table.name, other_table.name):
            # Disallow list fields that aren't related (these usually don't have
            # corresponding local columns)
            return True

        # if this_table.name == "datum_type" and other_table.name in [
        #     "constant",
        #     "datum",
        # ]:
        # Fields that are not allowed to be nested
        #    return True

        return False

    def _get_field_kwargs_for_property(self, prop):
        # Somewhat ugly method, mostly to decide if field is dump_only or required
        kwargs = super()._get_field_kwargs_for_property(prop)
        kwargs["data_key"] = self._get_key(prop)

        if isinstance(prop, Numeric):
            kwargs["allow_nan"] = True

        if isinstance(prop, RelationshipProperty):  # Relationship property
            cols = list(getattr(prop, "local_columns", []))
            kwargs["required"] = False
            for col in cols:
                if not col.nullable:
                    kwargs["required"] = True
            if prop.uselist:
                kwargs["required"] = False
            # # Empty collections can be represented by null values
            # if not kwargs["required"]:
            #     kwargs["allow_none"] = True

            return kwargs

        for col in prop.columns:
            is_integer = isinstance(col.type, Integer)
            # Special case for audit columns
            if col.name == "pgmemento_audit_id" and is_integer:
                kwargs["dump_only"] = True
                return kwargs

            if is_integer and col.primary_key:
                # Integer primary keys should be dump-only, probably
                # We could probably check for a default sequence
                # if we wanted to be general...
                kwargs["dump_only"] = True
            elif not col.nullable:
                kwargs["required"] = True

            dump_only = kwargs.get("dump_only", False)
            if not dump_only and not col.nullable:
                kwargs["required"] = True
            if dump_only:
                kwargs["required"] = False
            if col.default is not None:
                kwargs["required"] = False

            # We allow setting of UUIDs for now, but maybe we shouldn't
            if isinstance(col.type, postgresql.UUID):
                # This should be covered by the "default" case, but for some reason
                # server-set defaults don't show up
                kwargs["required"] = False

        return kwargs

    def _related_entity(self, prop):
        # If this is a relationship, return related entity
        if isinstance(prop, RelationshipProperty):
            return prop.mapper.entity
        return None

    def property2field(self, prop, **kwargs):
        """This override improves our handling of relationships"""
        if isinstance(prop, RelationshipProperty):
            return self._property2relationship(prop, **kwargs)
        else:
            return super().property2field(prop, **kwargs)

    def _property2relationship(self, prop, **kwargs):
        # The "name" is actually the name of the related model, NOT the name
        # of field
        cls = self._related_entity(prop)
        name = to_schema_name(cls.__name__)

        field_kwargs = self._get_field_kwargs_for_property(prop)
        field_kwargs.update(**kwargs)

        this_table = prop.parent.tables[0]
        if not allow_nest(this_table.name, prop.target.name):
            # Fields that are not allowed to be nested
            if prop.uselist:
                return RelatedList(PassThroughRelated, **field_kwargs)
            else:
                return PassThroughRelated(**field_kwargs)
        if prop.target.schema == "enum":
            # special carve-out for enums represented as foreign keys
            # (these should be stored in the 'enum' schema):
            return Enum(**field_kwargs)

        # Ignore fields that reference parent models in a nesting relationship
        exclude = []
        for p in cls.__mapper__.relationships:
            if self._should_exclude_field(p):
                # Fields that are already excluded do not need to be excluded again.
                continue
            id_ = self._get_field_name(p)
            if p.mapper.entity == prop.parent.entity:
                exclude.append(id_)

        return SmartNested(name, many=prop.uselist, exclude=exclude, **field_kwargs)
