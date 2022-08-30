from sqlalchemy.ext import automap
from sqlalchemy.ext.automap import generate_relationship
from os import path, environ
from sparrow.utils.logs import get_logger
from sparrow.birdbrain.mapper import DatabaseModelCache
from sparrow.birdbrain import DatabaseMapper

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


should_enable_cache = environ.get("SPARROW_CACHE_DATABASE_MODELS", "0").lower() in [
    "true",
    "1",
]


class AutomapError(Exception):
    pass


cache_path = path.join(path.expanduser("~"), ".sqlalchemy-cache", "sparrow-db-cache.pickle")

model_builder = DatabaseModelCache(cache_path)
BaseModel = model_builder.automap_base()

class SparrowDatabaseMapper(DatabaseMapper):
    automap_base = BaseModel

    def __init__(self, db, use_cache=True, reflect=True):
        # Apply the hotfix to the SQLAlchemy model.
        automap._is_many_to_many = _is_many_to_many
        super().__init__(db, generate_relationship=_gen_relationship)

        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#sqlalchemy.ext.automap.AutomapBase.prepare
        # TODO: add the process flow described below:
        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#generating-mappings-from-an-existing-metadata
        self.db = db
        self.automap_base = BaseModel
        if reflect:
            self.reflect_database(schemas=["vocabulary", "core_view", "tags", "public"], use_cache=use_cache)
