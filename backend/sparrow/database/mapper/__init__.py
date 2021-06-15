from sqlalchemy.schema import Table
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import generate_relationship
from sqlalchemy.ext.declarative import declarative_base
from os import path, makedirs
from sparrow_utils.logs import get_logger
from pickle import load, dump

# Drag in geographic types for database reflection
from geoalchemy2 import Geometry, Geography


from .shims import _is_many_to_many
from .util import (
    ModelCollection,
    TableCollection,
    classname_for_table,
    _classname_for_table,
    name_for_scalar_relationship,
    name_for_collection_relationship,
)
from .base import BaseModel

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


class SparrowDatabaseMapper:
    automap_base = None
    automap_error = None
    _models = None
    _tables = None
    metadata_pickle_filename = "sparrow_db_cache.pickle"
    cache_path = path.join(path.expanduser("~"), ".sqlalchemy_cache")

    def __init__(self, db):
        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#sqlalchemy.ext.automap.AutomapBase.prepare
        # TODO: add the process flow described below:
        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#generating-mappings-from-an-existing-metadata
        self.db = db
        self._reflect_database()

    def _reflect_database(self):
        cached_metadata = self._load_database_map()
        if cached_metadata is None:
            self.reflect_database()
            log.info("Caching database models")
            self._cache_database_map()

        else:
            log.info("Loading database models from cache")
            self.automap_base = declarative_base(
                bind=self.db.engine, metadata=cached_metadata
            )

        self._models = ModelCollection(self.automap_base.classes)
        self._tables = TableCollection(self._models)

    # https://stackoverflow.com/questions/41547778/sqlalchemy-automap-best-practices-for-performance/44607512
    def _cache_database_map(self):
        # save the metadata for future runs
        try:
            if not path.exists(self.cache_path):
                makedirs(self.cache_path)
            # make sure to open in binary mode - we're writing bytes, not str
            with open(
                path.join(self.cache_path, self.metadata_pickle_filename), "wb"
            ) as cache_file:
                dump(self.automap_base.metadata, cache_file)
        except:
            # couldn't write the file for some reason
            pass

    def _load_database_map(self):
        # We have hard-coded the cache file for now
        cached_metadata = None
        if path.exists(self.cache_path):
            try:
                with open(
                    path.join(self.cache_path, self.metadata_pickle_filename), "rb"
                ) as cache_file:
                    cached_metadata = load(file=cache_file)

            except IOError:
                # cache file not found - no problem
                pass
        return cached_metadata

    def reflect_database(self):
        # This stuff should be placed outside of core (one likely extension point).
        reflection_kwargs = dict(
            name_for_scalar_relationship=name_for_scalar_relationship,
            name_for_collection_relationship=name_for_collection_relationship,
            classname_for_table=_classname_for_table,
            generate_relationship=_gen_relationship,
        )

        for schema in ("vocabulary", "core_view", "tags"):
            # Reflect tables in schemas we care about
            # Note: this will not reflect views because they don't have
            # primary keys.
            log.info(f"Reflecting schema {schema}")
            BaseModel.metadata.reflect(bind=self.db.engine, schema=schema)
        log.info("Reflecting core tables")
        BaseModel.prepare(self.db.engine, reflect=True, **reflection_kwargs)

        self.automap_base = BaseModel

    def reflect_table(self, tablename, *column_args, **kwargs):
        """
        One-off reflection of a database table or view. Note: for most purposes,
        it will be better to use the database tables automapped at runtime in the
        `self.tables` object. However, this function can be useful for views (which
        are not reflected automatically), or to customize type definitions for mapped
        tables.

        A set of `column_args` can be used to pass columns to override with the mapper, for
        instance to set up foreign and primary key constraints.
        https://docs.sqlalchemy.org/en/13/core/reflection.html#reflecting-views
        """
        schema = kwargs.pop("schema", "public")
        meta = MetaData(schema=schema)
        tables = Table(
            tablename,
            meta,
            *column_args,
            autoload=True,
            autoload_with=self.db.engine,
            **kwargs,
        )
        return tables

    def reflect_view(self, tablename, *column_args, **kwargs):
        pass
        # schema = kwargs.pop("schema", "public")
        # meta = MetaData(self.engine,schema=schema)
        # ##meta.reflect(view=True)
        # log.info(meta.tables)
        # return meta.tables[tablename]

    def register_models(self, *models):
        # Could allow overriding name functions etc.
        self._models.register(*models)

    def automap_view(self, table_name, *column_args, **kwargs):
        """
        Views cannot be directly automapped, because they don't have primary keys.
        So we have to use a workaround of specifying a primary key ourselves.
        """
        tbl = self.reflect_table(table_name, *column_args, **kwargs)
        name = classname_for_table(tbl)
        return type(name, (BaseModel,), dict(__table__=tbl))
