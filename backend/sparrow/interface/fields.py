"""
Special additions to Marshmallow schemas for parsing and serializing
data from the Sparrow database.

Taken from https://gist.github.com/om-henners/97bc3a4c0b589b5184ba621fd22ca42e
"""
from marshmallow_sqlalchemy.fields import Related, Nested
from marshmallow.fields import Field, Raw
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape


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


class SmartNested(Nested):
    def _deserialize(self, value, attr=None, data=None, **kwargs):
        if isinstance(value, self.schema.opts.model):
            return value
        return super()._deserialize(value, attr, data, **kwargs)
