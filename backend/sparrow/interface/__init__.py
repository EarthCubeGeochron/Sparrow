from sparrow.plugins import SparrowCorePlugin
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, ModelSchema, exceptions
from marshmallow_sqlalchemy.fields import Related
from marshmallow.fields import Nested
from marshmallow_jsonschema import JSONSchema
from marshmallow_sqlalchemy.fields import get_primary_keys, ensure_list
from marshmallow.fields import Field, Raw
from marshmallow.decorators import pre_load
from sqlalchemy.exc import StatementError
from click import secho

from .converter import SparrowConverter, to_schema_name
from ..database.mapper.util import ModelCollection, classname_for_table


def _jsonschema_type_mapping(self):
    """TODO: this is just a shim"""
    return {'type': 'integer'}


Related._jsonschema_type_mapping = _jsonschema_type_mapping
Nested._jsonschema_type_mapping = _jsonschema_type_mapping

json_schema = JSONSchema()


class BaseMeta:
    model_converter = SparrowConverter
    # Needed for SQLAlchemyAutoSchema
    include_relationships = True
    load_instance = True


class BaseSchema(SQLAlchemyAutoSchema):
    def get_instance(self, data):
        """Gets pre-existing instances if they are available."""
        self.session.flush()
        if self.transient:
            return None

        # Filter on properties that actually have a local column
        filters = {}
        for k, v in data.items():
            field = getattr(self.opts.model, k)
            if getattr(field.prop, 'uselist', False):
                continue
            filters[k] = v
        ## Need to get relationship columns for primary keys!

        instance = None
        try:
            instance = self.session.query(self.opts.model).filter_by(**filters).first()
        except StatementError:
            pass
        if instance is None:
            return super().get_instance(data)
        #for attr, value in association_attrs.items():
        #    setattr(instance, attr, value)
        self.session.flush()
        return instance

    @pre_load
    def expand_primary_keys(self, value, **kwargs):
        print(value)
        try:
            # Typically, we are deserializing from a mapping of values
            return dict(**value)
        except TypeError:
            pass
        print(value)
        val_list = ensure_list(value)
        model = self.opts.model
        pk = get_primary_keys(model)
        assert len(pk) == len(val_list)
        res = {}
        for col, val in zip(pk, val_list):
            res[col.key] = val
        #print(value, res)
        #assert False
        return res

    def to_json_schema(model):
        return json_schema.dump(model)

    from .display import pretty_print


def model_interface(model, session=None):
    """
    Create a Marshmallow interface to a SQLAlchemy model
    """
    # Create a meta class
    metacls = type("Meta", (BaseMeta,), dict(
                    model=model,
                    sqla_session=session))

    schema_name = to_schema_name(model.__name__)
    try:
        # All conversion logic comes from ModelSchema
        return type(schema_name, (BaseSchema,), {'Meta': metacls})
    except exceptions.ModelConversionError as err:
        secho(type(err).__name__+": "+schema_name+" - "+str(err), fg='red')
        return None


class InterfaceCollection(ModelCollection):
    def register(self, *classes):
        for cls in classes:
            self._register_model(cls)

    def _register_model(self, cls):
        k = classname_for_table(cls.__table__)
        # Bail if we have a view
        if not hasattr(cls, '__mapper__'):
            return
        self.add(k, model_interface(cls))


class InterfacePlugin(SparrowCorePlugin):
    name = "schema-interface"

    def on_database_ready(self):
        iface = InterfaceCollection(self.app.database.model)
        db = self.app.database
        db.interface = iface

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
