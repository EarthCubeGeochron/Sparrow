from sqlalchemy.schema import Table
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import generate_relationship
from ...logs import get_logger
from ...exceptions import DatabaseMappingError

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
    if local_cls.__table__.schema is None and referred_cls.__table__.schema is not None:
        kw["backref"] = None
    kw["enable_typechecks"] = False

    # make use of the built-in function to actually return
    # the result.
    return generate_relationship(
        base, direction, return_fn, attrname, local_cls, referred_cls, **kw
    )


class AutomapError(Exception):
    pass


class MappedDatabaseMixin(object):
    automap_base = None
    automap_error = None
    __models__ = None
    __tables__ = None
    __inspector__ = None

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
        Tables = Table(
            tablename,
            meta,
            *column_args,
            autoload=True,
            autoload_with=self.engine,
            **kwargs,
        )
        log.info([c.name for c in Tables.columns])
        return Tables
    def reflect_view(self, tablename, *column_args, **kwargs):
        pass
        # schema = kwargs.pop("schema", "public")
        # meta = MetaData(self.engine,schema=schema)
        # ##meta.reflect(view=True)
        # log.info(meta.tables)
        # return meta.tables[tablename]

    def automap(self):
        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#sqlalchemy.ext.automap.AutomapBase.prepare
        # TODO: add the process flow described below:
        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#generating-mappings-from-an-existing-metadata

        BaseModel.query = self.session.query_property()
        BaseModel.db = self

        # This stuff should be placed outside of core (one likely extension point).
        reflection_kwargs = dict(
            name_for_scalar_relationship=name_for_scalar_relationship,
            name_for_collection_relationship=name_for_collection_relationship,
            classname_for_table=_classname_for_table,
            generate_relationship=_gen_relationship,
        )

        for schema in ("vocabulary", "core_view", "public"):
            # Reflect tables in schemas we care about
            # Note: this will not reflect views because they don't have
            # primary keys.
            log.info("Reflecting schema " + schema)
            BaseModel.metadata.reflect(
                bind=self.engine, schema=schema, **reflection_kwargs
            )
        BaseModel.prepare(self.engine, reflect=True, **reflection_kwargs)

        self.automap_base = BaseModel

        self.__models__ = ModelCollection(self.automap_base.classes)
        self.__tables__ = TableCollection(self.__models__)
        log.info("Finished automapping database")

    def register_models(self, *models):
        # Could allow overriding name functions etc.
        self.__models__.register(*models)

    def automap_view(db, table_name, *column_args, **kwargs):
        """
        Views cannot be directly automapped, because they don't have primary keys.
        So we have to use a workaround of specifying a primary key ourselves.
        """
        tbl = db.reflect_table(table_name, *column_args, **kwargs)
        name = classname_for_table(tbl)
        return type(name, (BaseModel,), dict(__table__=tbl))

    @property
    def table(self):
        """
        Map of all tables in the database as SQLAlchemy table objects
        """
        if self.__tables__ is None:
            self.automap()
        return self.__tables__

    @property
    def model(self):
        """
        Map of all tables in the database as SQLAlchemy models

        https://docs.sqlalchemy.org/en/latest/orm/extensions/automap.html
        """
        if self.__models__ is None:
            self.automap()
        return self.__models__

    @property
    def mapped_classes(self):
        return self.model
