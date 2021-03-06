"""
Special additions to Marshmallow schemas for parsing and serializing
data from the Sparrow database.

Taken from https://gist.github.com/om-henners/97bc3a4c0b589b5184ba621fd22ca42e
"""
from marshmallow_sqlalchemy.fields import Related, Nested
from marshmallow.fields import Field, Raw
from marshmallow.exceptions import ValidationError
from marshmallow.fields import UUID as _UUID
from marshmallow.utils import is_collection
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape
from collections.abc import Iterable
from .util import primary_key
from ..logs import get_logger

log = get_logger(__name__)


class UUID(_UUID):
    def _deserialize(self, value, attr, data, **kwargs):
        """We need to deserialize to a string to make SQLAlchemy happy"""
        return str(self._validated(value))


class JSON(Raw):
    pass


class Geometry(Field):
    """
    Field for for parsing and serializing a PostGIS geometry
    type to GeoJSON

    Use shapely and geoalchemy2 to serialize / deserialize a point
    Does make a big assumption about the data being spat back out as
    JSON, but what the hey.
    """

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        return mapping(to_shape(value))

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        return from_shape(shape(value))


class Enum(Related):
    """
    Enums are represented by a `Related` field, but we want to potentially
    be able to revise/extend this later without breaking external APIs.
    """

    pass


class NullableRelated(Related):
    def __init__(self, *args, **kwargs):
        kwargs["allow_none"] = True
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr=None, data=None, **kwargs):
        if value is None:
            if self.many:
                return []
            return None
        return super()._deserialize(value, attr, data, **kwargs)


class SmartNested(Nested, Related):
    """This field allows us to resolve relationships as either primary keys or nested models."""

    # https://github.com/marshmallow-code/marshmallow/blob/dev/src/marshmallow/fields.py
    # TODO: better conformance of this field to Marshmallow's OpenAPI schema generation
    # https://apispec.readthedocs.io/en/latest/using_plugins.html
    def __init__(
        self, name, *, only=None, exclude=(), many=False, unknown=None, **field_kwargs
    ):
        super(Nested, self).__init__(
            name,
            only=only,
            exclude=exclude,
            many=many,
            unknown=unknown,
            **field_kwargs,
        )
        super(Related, self).__init__(**field_kwargs)
        self._many = many
        self._instances = set()
        self.allow_none = True

    def _deserialize(self, value, attr=None, data=None, **kwargs):
        if isinstance(value, self.schema.opts.model):
            return value
        # Better error message for collections.
        if not is_collection(value) and self._many:
            raise ValidationError("Provided a single object for a collection field")
        if is_collection(value) and not self._many:
            raise ValidationError("Provided a collection for a instance field")

        return super()._deserialize(value, attr, data, **kwargs)

    def _serialize_related_key(self, value):
        """Serialize the primary key for a related model. In the (common) special
        case of a 1-column primary key, return just the value of that column; otherwise,
        return a map of {column_name: value}"""
        key = primary_key(value)
        if len(key.keys()) == 1:
            return list(key.values())[0]
        return key

    def _serialize_instance(self, value):
        if value is None:
            return None
        self._instances.add(value)
        return self._serialize_related_key(value)

    def _copy_config(self, key):
        """Copy configuration from root model"""
        if hasattr(self.root, key):
            setattr(self.schema, key, getattr(self.root, key))

    def _serialize(self, value, attr, obj):
        # return ret if len(ret) > 1 else list(ret)[0]
        # return super(Nested, self)._serialize(value, attr, obj)
        # Don't allow nesting for now...

        # Pass through allowed_nests configuration to child schema
        self._copy_config("allowed_nests")
        self._copy_config("_show_audit_id")

        other_name = self.related_model.__table__.name
        _allowed = self.root.allowed_nests
        if other_name in _allowed or _allowed == "all":
            # Serialize as nested
            return super(Nested, self)._serialize(value, attr, obj)

        # If we don't want to nest
        if self._many:
            return [self._serialize_instance(v) for v in value]
        return self._serialize_instance(value)
