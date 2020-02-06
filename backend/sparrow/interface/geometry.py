"""
Special additions to Marshmallow schemas for parsing and serializing
to GeoJSON

Taken from https://gist.github.com/om-henners/97bc3a4c0b589b5184ba621fd22ca42e
"""
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape
from marshmallow.fields import Field

class GeometryField(Field):
    """
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
