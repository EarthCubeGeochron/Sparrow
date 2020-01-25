from marshmallow_sqlalchemy import ModelConverter
from marshmallow.fields import Nested
from geoalchemy2 import Geography, Geometry
from sqlalchemy.orm import RelationshipProperty
from stringcase import pascalcase

from .geometry import GeometryField

def to_schema_name(name):
    return pascalcase(name+"_schema")


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

    def fields_for_model(self, model, **kwargs):
        print(" ")
        print(model)
        return super().fields_for_model(model, **kwargs)

    def property2field(self, prop, **kwargs):
        print("  ",prop)
        if isinstance(prop, RelationshipProperty):
            # Get the class for this relationship
            cls = prop.mapper.class_
            name = to_schema_name(cls.__name__)
            # Exclude primary key columns from nesting
            exclude = [c.name for c in prop.remote_side]
            return Nested(name, many=prop.uselist, exclude=exclude)
        return super().property2field(prop, **kwargs)
