from macrostrat.database import DatabaseMapper
from macrostrat.database.mapper import DatabaseModelCache
from macrostrat.database.mapper.utils import ModelCollection, TableCollection
from macrostrat.utils.logs import get_logger
from sqlalchemy.ext import automap
from sqlalchemy.ext.automap import generate_relationship

from .shims import _is_many_to_many

log = get_logger(__name__)


def _gen_relationship(
    base, direction, return_fn, attrname, local_cls, referred_cls, **kw
):
    support_schemas = ["vocabulary", "core_view"]
    if (
        local_cls.__table__.schema in support_schemas
        and referred_cls.__table__.schema is None
    ):
        # Don't create relationships on vocabulary and core_view models back to the main schema
        return
    return generate_relationship(
        base, direction, return_fn, attrname, local_cls, referred_cls, **kw
    )


class AutomapError(Exception):
    pass


BaseModel = DatabaseModelCache().automap_base()


class SparrowDatabaseMapper(DatabaseMapper):
    automap_base = BaseModel

    def __init__(self, db, reflect=True):
        # Apply the hotfix to the SQLAlchemy model.
        automap._is_many_to_many = _is_many_to_many
        super().__init__(db, generate_relationship=_gen_relationship)

        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#sqlalchemy.ext.automap.AutomapBase.prepare
        # TODO: add the process flow described below:
        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#generating-mappings-from-an-existing-metadata
        self.db = db
        self.automap_base = BaseModel
        if reflect:
            self.reflect_database(schemas=["vocabulary", "core_view", "tags", "public"])

    def reflect_database(self, schemas=["public"]):
        base = self.automap_base
        # Models are prepared once, after the supporting schemas are reflected,
        # so that pre-declared models find their columns.
        for schema in schemas:
            if schema == "public":
                continue
            log.info(f"Reflecting schema {schema}")
            base.metadata.reflect(bind=self.db.engine, schema=schema)
        base.prepare(autoload_with=self.db.engine, **self.reflection_kwargs)
        self._reflected_schemas.update(schemas)

        self._models = ModelCollection(base.classes)
        self._tables = TableCollection(self._models)
