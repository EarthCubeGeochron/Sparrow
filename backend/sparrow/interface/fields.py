"""
Special additions to Marshmallow schemas for parsing and serializing
data from the Sparrow database.

Taken from https://gist.github.com/om-henners/97bc3a4c0b589b5184ba621fd22ca42e
"""
from marshmallow_sqlalchemy.fields import Related, Nested
from marshmallow.fields import Field
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape


class EnumField(Related):
    """
    Enums are represented by a `Related` field, but we want to potentially
    be able to revise/extend this later without breaking external APIs.
    """
    pass


class GeometryField(Field):
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

    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        return from_shape(shape(value))


class SmartNested(Nested):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

    def serialize(self, attr, obj, accessor=None):
        #if attr not in obj.__dict__:
        #    return {"id": int(getattr(obj, attr + "_id"))}
        return super().serialize(attr, obj, accessor)
