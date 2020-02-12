from sparrow.plugins import SparrowCorePlugin
from marshmallow_sqlalchemy import ModelSchema, exceptions
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow_jsonschema import JSONSchema
from click import secho

from .converter import SparrowConverter, to_schema_name
from .display import pretty_print
from ..database.mapper.util import ModelCollection, classname_for_table


def _jsonschema_type_mapping(self):
    return {'type': 'integer'}


Related._jsonschema_type_mapping = _jsonschema_type_mapping
Nested._jsonschema_type_mapping = _jsonschema_type_mapping

json_schema = JSONSchema()


def to_json_schema(model):
    return json_schema.dump(model)


def model_interface(model, session=None):
    """
    Create a Marshmallow interface to a SQLAlchemy model
    """
    # Create a meta class
    metacls = type("Meta", (), dict(
        model=model,
        model_converter=SparrowConverter,
        sqla_session=session
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
            self._register_table(cls)

    def _register_table(self, cls):
        k = classname_for_table(cls.__table__)
        # Bail if we have a view
        if not hasattr(cls, '__mapper__'):
            return
        self.add(k, model_interface(cls))



class InterfacePlugin(SparrowCorePlugin):
    name = "schema-interface"

    def on_database_ready(self):
        iface = InterfaceCollection(self.app.database.model)
        self.app.interface = iface

    def on_setup_cli(self, cli):
        from .cli import show_interface
        cli.add_command(show_interface)


def load_data(mapping):
    from ..app import construct_app
    app, db = construct_app()
    print(mapping)


# transient load
# https://marshmallow-sqlalchemy.readthedocs.io/en/latest/recipes.html#smart-nested-field
# schema().load({}, transient=True)
