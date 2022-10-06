from typing import List
from macrostrat.database.mapper.utils import ModelCollection
from marshmallow.utils import RAISE
from .interface import model_interface, InterfaceCollection
from .schema import ModelSchema, BaseMeta

from .schema_checking import get_automap_base, get_model
from .display import print_key


def get_cached_models():
    """Get a collection of all Sparrow database models available for importing"""
    base = get_automap_base()
    return ModelCollection(base.classes)


def get_all_loader_schemas():
    """Get a collection of all Sparrow database loader schemas"""
    models = get_cached_models()
    coll = InterfaceCollection(models)
    return coll


def get_loader_schema(name):
    """Get the loader schema for a Sparrow database model"""
    return getattr(get_all_loader_schemas(), name)


def validate_data(model_name, data):
    """Check a dictionary of data against a Sparrow database model"""

    interface = get_loader_schema(model_name)
    return interface(transient=True).load(data, unknown=RAISE)


def show_loader_schemas(*schemas: List[str], nest_depth=0):
    """Print the loader schema for a Sparrow database model"""
    models = get_cached_models()
    coll = InterfaceCollection(models)

    if len(schemas) == 0:
        schemas = coll.keys()

    for name in schemas:
        schema = getattr(coll, name)
        schema().pretty_print(nested=nest_depth, model_alias=name)
        print()
    print_key()


def show_loader_schema(schema: str, nest_depth=0):
    """Print the loader schema for a Sparrow database model"""
    show_loader_schemas(schema, nest_depth=nest_depth)
