from marshmallow_sqlalchemy import ModelConverter
from marshmallow.fields import Nested

from geoalchemy2 import Geography, Geometry
from sqlalchemy.orm import RelationshipProperty
from stringcase import pascalcase

from .geometry import GeometryField


def to_schema_name(name):
    return pascalcase(name+"_schema")


class SmartNested(Nested):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    def serialize(self, attr, obj, accessor=None):
        #if attr not in obj.__dict__:
        #    return {"id": int(getattr(obj, attr + "_id"))}
        return super().serialize(attr, obj, accessor)


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
        return super().fields_for_model(model, **kwargs)

    def property2field(self, prop, **kwargs):
        #print("  ",prop)
        if isinstance(prop, RelationshipProperty):
            # Get the class for this relationship
            cls = prop.mapper.class_
            name = to_schema_name(cls.__name__)

            this_table = prop.parent.mapped_table.name

            # Exclude field based on table name
            if prop.target.name == 'data_file_link':
                return None

            # if prop.backref:
            #     return None

            if prop.target.name == 'session':
                if this_table not in ["project", "sample"]:
                    return None

            if prop.target.name == 'analysis':
                if this_table != 'session':
                    return None

            # Projects cannot be nested by anything...
            if prop.target.name == 'project':
                return None

            # Materials have a self-referential relationship which is given
            # a collection, but this shouldn't be serializable
            if this_table == 'material' and prop.target.name == 'material' and prop.uselist:
                return None

            # if prop.entity.name == 'analysis':
            #     if prop.parent.name not in ["session"]:
            #         return None

            # Exclude foreign key columns from nesting
            #exclude = [c.name for c in prop.remote_side]
            exclude = []
            return SmartNested(name, many=prop.uselist, exclude=exclude)
        return super().property2field(prop, **kwargs)
