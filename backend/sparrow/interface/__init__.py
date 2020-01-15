from sparrow.plugins import SparrowCorePlugin
from marshmallow_sqlalchemy import ModelSchema, exceptions
from marshmallow_sqlalchemy.fields import Related
from marshmallow_jsonschema import JSONSchema
from stringcase import pascalcase
from ..database.helpers import ModelCollection, classname_for_table
from click import echo, secho

def _jsonschema_type_mapping(self):
    return {
        'type': 'integer',
    }

Related._jsonschema_type_mapping = _jsonschema_type_mapping

def to_schema_name(name):
    return pascalcase(name+"_schema")

json_schema = JSONSchema()

def to_json_schema(model):
    return json_schema.dump(model)

def model_interface(model):
    """
    Create a Marshmallow interface to a SQLAlchemy model
    """
    # Create a meta class
    metacls = type("Meta", (), dict(model=model))

    schema_name = to_schema_name(model.__name__)
    try:
        return type(
            schema_name, (ModelSchema,), dict(
                Meta=metacls,
                as_jsonschema=to_json_schema
            ))
    except exceptions.ModelConversionError as err:
        secho(schema_name+": "+str(err), fg='red')
        return None

class InterfaceCollection(ModelCollection):
    def register(self, *classes):
        for cls in classes:
            k = classname_for_table(cls.__table__)
            try:
                self.add(k, model_interface(cls))
            except Exception as err:
                secho(str(err))


class InterfacePlugin(SparrowCorePlugin):
    name = "schema-interface"

    def on_database_ready(self):
        iface = InterfaceCollection(self.app.database.model)
        self.app.interface = iface
