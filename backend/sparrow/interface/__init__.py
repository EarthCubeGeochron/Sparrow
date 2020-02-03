from sparrow.plugins import SparrowCorePlugin
from marshmallow_sqlalchemy import ModelSchema, exceptions
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow.exceptions import RegistryError
from marshmallow_jsonschema import JSONSchema
from .converter import SparrowConverter, to_schema_name
from ..database.helpers import ModelCollection, classname_for_table
from click import echo, secho, style
from textwrap import indent

def _jsonschema_type_mapping(self):
    return {'type': 'integer'}

Related._jsonschema_type_mapping = _jsonschema_type_mapping
Nested._jsonschema_type_mapping = _jsonschema_type_mapping

json_schema = JSONSchema()

styled_key = lambda k: style("• ", dim=True)+k+style(": ", dim=True)

def to_json_schema(model):
    return json_schema.dump(model)

def pretty_print(model, prefix="", key=None):
    new_prefix = prefix[0:len(prefix)-3]
    if key is not None:
        new_prefix += styled_key(key)
    print(new_prefix+model.__class__.__name__)
    for k,v in model._declared_fields.items():

        if isinstance(v, Nested):
            if len(prefix) < 6:
                try:
                    pretty_print(v.schema, prefix=prefix+"   ", key=k)
                except ValueError as err:
                    echo(v.schema.exclude)
                    echo(prefix+styled_key(k)+style(str(err), fg="red"))
                except RegistryError as err:
                    pass
                except AttributeError as err:
                    echo(prefix+styled_key(k)+style(str(err), fg="red"))
        else:
            classname = v.__class__.__name__
            nfill = 32-len(k)-len(classname)
            echo(prefix+styled_key(k)+style("."*nfill,dim=True)+style(classname, fg="cyan", dim=True))

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


def load_data(mapping):
    from ..app import construct_app
    app, db = construct_app()
    print(mapping)


# transient load
# https://marshmallow-sqlalchemy.readthedocs.io/en/latest/recipes.html#smart-nested-field
# schema().load({}, transient=True)
