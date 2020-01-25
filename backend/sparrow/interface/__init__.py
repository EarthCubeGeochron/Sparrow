from sparrow.plugins import SparrowCorePlugin
from marshmallow_sqlalchemy import ModelSchema, exceptions
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow_jsonschema import JSONSchema
from .converter import SparrowConverter, to_schema_name
from ..database.helpers import ModelCollection, classname_for_table
from click import secho
from textwrap import indent

def _jsonschema_type_mapping(self):
    return {'type': 'integer'}

Related._jsonschema_type_mapping = _jsonschema_type_mapping
Nested._jsonschema_type_mapping = _jsonschema_type_mapping


json_schema = JSONSchema()


def to_json_schema(model):
    return json_schema.dump(model)

def pretty_print(model, prefix=""):
    print(prefix+model.__class__.__name__)
    for k,v in model.dump_fields.items():
        print(k, isinstance(v, Nested))
        if isinstance(v, Nested):
            print(f"{prefix}{k}:")
            pretty_print(v.schema, prefix=prefix+"  ")
            continue
        print(f"{prefix}  {k}: {v.__class__.__name__}")

def model_interface(model):
    """
    Create a Marshmallow interface to a SQLAlchemy model
    """
    # Create a meta class
    metacls = type("Meta", (), dict(
        model=model,
        model_converter=SparrowConverter
    ))

    schema_name = to_schema_name(model.__name__)
    try:
        return type(
            schema_name, (ModelSchema,), dict(
                Meta=metacls,
                as_jsonschema=to_json_schema,
                pretty_print=pretty_print
            ))
    except exceptions.ModelConversionError as err:
        secho(type(err).__name__+": "+schema_name+" - "+str(err), fg='red')
        return None


class InterfaceCollection(ModelCollection):
    def register(self, *classes):
        for cls in classes:
            k = classname_for_table(cls.__table__)
            try:
                self.add(k, model_interface(cls))
            except Exception as err:
                secho(str(err), fg='red')


class InterfacePlugin(SparrowCorePlugin):
    name = "schema-interface"

    def on_database_ready(self):
        iface = InterfaceCollection(self.app.database.model)
        self.app.interface = iface


def load_data(mapping):
    from ..app import construct_app
    app, db = construct_app()
    print(mapping)


# transient load
# https://marshmallow-sqlalchemy.readthedocs.io/en/latest/recipes.html#smart-nested-field
# schema().load({}, transient=True)
