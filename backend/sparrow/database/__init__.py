from click import echo, secho
from os import environ

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Table
from sqlalchemy.sql import ClauseElement
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
    return "_"+referred_cls.__name__.lower()

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
        self.session = sessionmaker(bind=self.engine)()
        self.automap_base = None
        self.__model_collection__ = None
        self.__table_collection__ = None
        # We're having trouble lazily automapping
        try:
            self.automap()
        except Exception as err:
            echo("Could not automap at database initialization", err=True)
            secho(str(err), fg='red')

    def exec_sql(self, *args):
        run_sql_file(self.session, *args)

    def exec_query(self, *args):
        run_query(self.session, *args)

    def reflect_table(self, tablename, schema='public', **kwargs):
        """
        Use the automapped `table` object instead.
        """
        meta = MetaData(schema=schema)
        return Table(tablename, meta,
            autoload=True, autoload_with=self.engine, **kwargs)

    def automap(self):
        Base.prepare(self.engine, reflect=True,
            name_for_scalar_relationship=name_for_scalar_relationship)

        self.automap_base = Base
        # Database models we have extended with our own functions
        # (we need to add these to the automapped classes since they are not
        #  included by default)
        additional_models = {t.__tablename__:t for t in extended_models}
        self.__model_collection__ = JointModelCollection(
            self.automap_base.classes,
            additional_models)
        self.__table_collection__ = TableCollection(
            self.__model_collection__)

    @property
    def table(self):
        """
        Map all tables in the database to SQLAlchemy table objects
        """
        if self.__table_collection__ is None:
            self.automap()
        return self.__table_collection__

    @property
    def model(self):
        """
        Map all tables in the database to SQLAlchemy models

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

    def get_or_create(self, model, defaults=None, **kwargs):
        """
        Get an instance of a model, or create it if it doesn't
        exist.
        """
        if isinstance(model, str):
            model = getattr(self.model, model)
        return get_or_create(self.session, model, defaults=None, **kwargs)

    def initialize(self, drop=False):
        secho("Creating core schema...", bold=True)

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
