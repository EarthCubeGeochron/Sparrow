from click import echo, secho
from os import environ

from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Table, ForeignKey, Column
from sqlalchemy.sql import ClauseElement
from sqlalchemy.types import Integer
from pathlib import Path

from ..app import App
from ..models import Base, User, Project
from ..util import run_sql_file, run_query, relative_path
from .helpers import (
    JointModelCollection, TableCollection, get_or_create)

extended_models = [User, Project]

metadata = MetaData()

# For automapping
def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
    return "_"+referred_cls.__table__.name.lower()

def classname_for_table(table):
    if table.schema is not None:
        return f"{table.schema}_{table.name}"
    return table.name

def _classname_for_table(cls, table_name, table):
    # We have to be fancy for SQLAlchemy
    return classname_for_table(table)

class Database:
    def __init__(self, cfg=None):
        """
        We can pass a connection string, a **Flask** application object
        with the appropriate configuration, or nothing, in which
        case we will try to infer the correct database from
        the SPARROW_BACKEND_CONFIG file, if available.
        """
        self.config = None
        if cfg is None:
            # Set config from environment variable
            cfg = App(__name__)
        if hasattr(cfg,'config'):
            cfg = cfg.config
        self.config = cfg
        db_conn = self.config.get("DATABASE")
        # Override with environment variable
        envvar = environ.get("SPARROW_DATABASE", None)
        if envvar is not None:
            db_conn = envvar
        self.engine = create_engine(db_conn)
        metadata.create_all(bind=self.engine)
        self.meta = metadata
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.automap_base = None
        self.__model_collection__ = None
        self.__table_collection__ = None
        self.__inspector__ = None
        # We're having trouble lazily automapping
        try:
            self.automap()
        except Exception as err:
            echo("Could not automap at database initialization", err=True)

    def exec_sql(self, *args):
        run_sql_file(self.session, *args)

    def exec_query(self, *args):
        run_query(self.session, *args)

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
        schema = kwargs.pop('schema', 'public')
        meta = MetaData(schema = schema)
        return Table(tablename, meta, *column_args,
            autoload=True, autoload_with=self.engine, **kwargs)

    def automap(self):
        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#sqlalchemy.ext.automap.AutomapBase.prepare
        # TODO: add the process flow described below:
        # https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html#generating-mappings-from-an-existing-metadata
        Base.query = self.session.query_property()

        # This stuff should be placed outside of core (one likely extension point).
        Base.prepare(self.engine, reflect=True,
            name_for_scalar_relationship=name_for_scalar_relationship,
            classname_for_table=_classname_for_table)
        Base.metadata.reflect(bind=self.engine, schema='vocabulary')
        Base.metadata.reflect(bind=self.engine, schema='core_view')

        self.automap_base = Base
        # Database models we have extended with our own functions
        # (we need to add these to the automapped classes since they are not
        #  included by default)

        # Automap the core_view.datum relationship
        cls = self.automap_view("datum",
            Column("datum_id", Integer, primary_key=True),
            Column("analysis_id", Integer, ForeignKey(self.automap_base.classes.analysis.__table__.c.id)),
            Column("session_id", Integer, ForeignKey(self.automap_base.classes.session.__table__.c.id)),
            schema='core_view')
        extended_models.append(cls)

        additional_models = {classname_for_table(t.__table__):t for t in extended_models}
        self.__model_collection__ = JointModelCollection(
            self.automap_base.classes,
            additional_models)
        self.__table_collection__ = TableCollection(
            self.__model_collection__)

    def automap_view(db, table_name, *column_args, **kwargs):
        """
        Views cannot be directly automapped, because they don't have primary keys.
        So we have to use a workaround of specifying a primary key ourselves.
        """
        tbl = db.reflect_table(table_name, *column_args, **kwargs)
        name = classname_for_table(tbl)
        return type(name, (Base,), dict(__table__ = tbl))

    @property
    def inspector(self):
        if self.__inspector__ is None:
            self.__inspector__ = inspect(self.engine)
        return self.__inspector__

    def entity_names(self, **kwargs):
        """
        Returns an iterator of names of *schema objects*
        (both tables and views) from a the database.
        """
        yield from self.inspector.get_table_names(**kwargs)
        yield from self.inspector.get_view_names(**kwargs)

    @property
    def table(self):
        """
        Map of all tables in the database as SQLAlchemy table objects
        """
        if self.__table_collection__ is None:
            self.automap()
        return self.__table_collection__

    @property
    def model(self):
        """
        Map of all tables in the database as SQLAlchemy models

        https://docs.sqlalchemy.org/en/latest/orm/extensions/automap.html
        """
        if self.__model_collection__ is None:
            self.automap()
        return self.__model_collection__

    @property
    def mapped_classes(self):
        return self.model

    def get(self, model, *args, **kwargs):
        if isinstance(model, str):
            model = getattr(self.model, model)
        return self.session.query(model).get(*args,**kwargs)

    def get_or_create(self, model, **kwargs):
        """
        Get an instance of a model, or create it if it doesn't
        exist.
        """
        if isinstance(model, str):
            model = getattr(self.model, model)
        return get_or_create(self.session, model, **kwargs)

    def initialize(self, drop=False):
        secho("Creating core schema...", bold=True)

        if drop:
            fp = relative_path(__file__, "procedures", "drop-all-tables.sql")
            self.exec_sql(fp)

        p = Path(relative_path(__file__, "fixtures"))
        filenames = list(p.glob("*.sql"))
        filenames.sort()
        pretty_print = lambda x: secho(x, fg='cyan', bold=True)

        for fn in filenames:
            pretty_print(fn.name)
            self.exec_sql(str(fn))

        init_sql = self.config.get("INIT_SQL", None)
        if init_sql is not None:
            secho("\nCreating schema extensions...", bold=True)
            for s in init_sql:
                pretty_print(Path(s).name)
                self.exec_sql(s)
