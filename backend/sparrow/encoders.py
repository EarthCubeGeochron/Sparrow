from json import JSONEncoder as BaseJSONEncoder
from datetime import datetime
from decimal import Decimal
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping


def to_geojson(wkb):
    return mapping(to_shape(wkb))


class JSONEncoder(BaseJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, WKBElement):
            return to_geojson(obj)
        super().default(obj)
