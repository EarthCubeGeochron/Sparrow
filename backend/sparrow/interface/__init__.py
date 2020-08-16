from sparrow.plugins import SparrowCorePlugin
from marshmallow_sqlalchemy import exceptions
from click import secho

from .schema import ModelSchema, BaseMeta
from .util import to_schema_name
from ..database.mapper.util import ModelCollection, classname_for_table

from sparrow import get_logger

log = get_logger(__name__)


def model_interface(model, session=None) -> ModelSchema:
    """
    Create a Marshmallow interface to a SQLAlchemy model
    """
    # Create a meta class
    metacls = type("Meta", (BaseMeta,), dict(model=model, sqla_session=session))

    schema_name = to_schema_name(model.__name__)
    try:
        # All conversion logic comes from ModelSchema
        return type(schema_name, (ModelSchema,), {"Meta": metacls})
    except exceptions.ModelConversionError as err:
        secho(type(err).__name__ + ": " + schema_name + " - " + str(err), fg="red")
        return None


class InterfaceCollection(ModelCollection):
    def register(self, *classes):
        for cls in classes:
            self._register_model(cls)

    def _register_model(self, cls):
        k = classname_for_table(cls.__table__)
        # Bail if we have a view
        if not hasattr(cls, "__mapper__"):
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
