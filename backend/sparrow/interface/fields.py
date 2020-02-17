"""
Special additions to Marshmallow schemas for parsing and serializing
data from the Sparrow database.

Taken from https://gist.github.com/om-henners/97bc3a4c0b589b5184ba621fd22ca42e
"""
from marshmallow_sqlalchemy.fields import (
    Related, Nested, get_primary_keys, ensure_list
)
from marshmallow.fields import Field, Raw
from marshmallow.decorators import pre_load
from marshmallow.exceptions import ValidationError
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape
from collections import Mapping

from ..database.util import get_or_create

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

    def _deserialize(self, value, attr, data):
        if value is None:
            return None
        return from_shape(shape(value))


class Enum(Related):
    """
    Enums are represented by a `Related` field, but we want to potentially
    be able to revise/extend this later without breaking external APIs.
    """
    pass

from marshmallow import missing

class SmartNested(Nested):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

    def serialize(self, attr, obj, accessor=None):
        #if attr not in obj.__dict__:
        #    return {"id": int(getattr(obj, attr + "_id"))}
        return super().serialize(attr, obj, accessor)

    # @pre_load
    # def expand_primary_keys(self, value, **kwargs):
    #     try:
    #         # Typically, we are deserializing from a mapping of values
    #         return dict(**value)
    #     except TypeError:
    #         pass
    #     val_list = ensure_list(value)
    #     model = self.schema.opts.model
    #     pk = get_primary_keys(model)
    #     assert len(pk) == len(val_list)
    #     res = {}
    #     for col, val in zip(pk, val_list):
    #         res[col.key] = val
    #     return res

    # def deserialize_as_primary_key(self, value, attr=None, data=None, **kwargs):
    #     # Try to serialize as a primary key
    #     val_list = ensure_list(value)
    #     model = self.schema.opts.model
    #     pk = get_primary_keys(model)
    #     assert len(pk) == len(val_list)
    #     res = {}
    #     for col, val in zip(pk, val_list):
    #         res[col.key] = val
    #     print(res)
    #     return super()._deserialize(res, attr, data, **kwargs)

    def _deserialize(self, value, attr=None, data=None, **kwargs):
        # Typically, we are deserializing from a mapping of values,
        # and this is what the Nested field is set up to accept.
        kwargs['parent'] = self.parent
        val = super()._deserialize(value, attr, data, **kwargs)
        print("Deserializing as: ", val)
        # if isinstance(val, list):
        return val
