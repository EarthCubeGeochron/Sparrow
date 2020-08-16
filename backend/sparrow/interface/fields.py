"""
Special additions to Marshmallow schemas for parsing and serializing
data from the Sparrow database.

Taken from https://gist.github.com/om-henners/97bc3a4c0b589b5184ba621fd22ca42e
"""
from marshmallow_sqlalchemy.fields import Related, Nested
from marshmallow.fields import Field, Raw
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape
from collections.abc import Iterable
from .util import primary_key
from ..logs import get_logger

log = get_logger(__name__)


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


class SmartNested(Nested, Related):
    # https://github.com/marshmallow-code/marshmallow/blob/dev/src/marshmallow/fields.py
    def __init__(
        self, name, *, only=None, exclude=(), many=False, unknown=None, **field_kwargs
    ):
        super(Nested, self).__init__(
            name, only=only, exclude=exclude, many=many, unknown=unknown, **field_kwargs
        )
        super(Related, self).__init__(**field_kwargs)
        self._instances = set()

    def _deserialize(self, value, attr=None, data=None, **kwargs):
        if isinstance(value, self.schema.opts.model):
            return value
        return super(Nested, self)._deserialize(value, attr, data, **kwargs)

    def _serialize_related_key(self, value):
        """Serialize the primary key for a related model. In the (common) special
        case of a 1-column primary key, return just the value of that column; otherwise,
        return a map of {column_name: value}"""
        key = primary_key(value)
        if len(key.keys()) == 1:
            return list(key.values())[0]
        return key

    def _serialize_instance(self, value):
        self._instances.add(value)
        return self._serialize_related_key(value)

    def _serialize(self, value, attr, obj):
        # ret = [prop.key for prop in self.related_keys]
        # ret = {prop.key: getattr(value, prop.key, None) for prop in self.related_keys}
        # return ret if len(ret) > 1 else list(ret)[0]
        # return super(Nested, self)._serialize(value, attr, obj)
        # Don't allow nesting for now...
        if value is None:
            return None

        if isinstance(value, Iterable):
            return [self._serialize_instance(v) for v in value]
        return self._serialize_instance(value)
