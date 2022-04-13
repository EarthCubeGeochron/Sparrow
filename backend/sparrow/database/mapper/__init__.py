from typing_extensions import Self
from sqlalchemy.schema import Table
from sqlalchemy import MetaData
from sqlalchemy.ext import automap
from sqlalchemy.ext.automap import automap_base, generate_relationship
from sqlalchemy.ext.declarative import declarative_base
from os import path, makedirs
from sparrow.utils.logs import get_logger
from sqlalchemy.ext.automap import automap_base
from pickle import load, dump
from sparrow.birdbrain.mapper import DatabaseModelCacher
from sparrow.birdbrain.mapper.base import ModelHelperMixins
from sparrow.birdbrain import DatabaseMapper

# Drag in geographic types for database reflection
from geoalchemy2 import Geometry, Geography
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


model_builder = DatabaseModelCacher()

BaseModel = model_builder()

class SparrowDatabaseMapper(DatabaseMapper):
    automap_base = None
    automap_error = None
    _models = None
    _tables = None

    def __init__(self, db, use_cache=True, reflect=True):
        # Apply the hotfix to the SQLAlchemy model.
        automap._is_many_to_many = _is_many_to_many

        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#sqlalchemy.ext.automap.AutomapBase.prepare
        # TODO: add the process flow described below:
        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#generating-mappings-from-an-existing-metadata
        self.db = db
        self.automap_base = BaseModel
        if reflect:
            self.reflect_database(use_cache=use_cache)
