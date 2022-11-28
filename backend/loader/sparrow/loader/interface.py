from marshmallow_sqlalchemy import exceptions

from .schema import ModelSchema, BaseMeta
from .util import to_schema_name

from macrostrat.database.mapper.utils import ModelCollection, classname_for_table
from macrostrat.utils import get_logger

log = get_logger(__name__)


def model_interface(model, session=None) -> ModelSchema:
    """
    Create a Marshmallow interface to a SQLAlchemy model
    """
    # Create a meta class
    metacls = type(
        "Meta",
        (BaseMeta,),
        dict(
            model=model,
            sqla_session=session,
            load_instance=False,
            include_relationships=True,
        ),
    )

    schema_name = to_schema_name(model.__name__)
    try:
        # All conversion logic comes from ModelSchema
        return type(schema_name, (ModelSchema,), {"Meta": metacls})
    except exceptions.ModelConversionError as err:
        log.error(type(err).__name__ + ": " + schema_name + " - " + str(err))
        return None


class InterfaceCollection(ModelCollection):
    def register(self, *classes):
        for cls in classes:
            # Don't build model for spatial_ref_sys PostGIS table
            # TODO: we could probably generalize this.
            if cls.__table__.name == "spatial_ref_sys":
                continue
            if cls.__table__.schema == "enum":
                continue
            self._register_model(cls)

    def _register_model(self, cls):
        k = classname_for_table(cls.__table__)
        # Bail if we have a view
        if not hasattr(cls, "__mapper__"):
            return
        self.add(k, model_interface(cls))
