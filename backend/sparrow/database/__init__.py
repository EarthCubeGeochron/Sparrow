from contextlib import contextmanager
from pathlib import Path
from click import echo, secho
from os import environ

from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.schema import Table, ForeignKey, Column
from sqlalchemy.types import Integer

# Drag in geographic types for database reflection
from geoalchemy2 import Geometry, Geography

from ..logs import get_logger
from ..util import run_sql_file, run_query, relative_path
from ..models import Base, User, Project, Session
from .helpers import (
    ModelCollection, TableCollection, get_or_create,
    classname_for_table, _classname_for_table)
from .fixes import _is_many_to_many

metadata = MetaData()

log = get_logger(__name__)

class AutomapError(Exception):
    pass

# For automapping
def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
    return "_"+referred_cls.__table__.name.lower()

class Database:
    def __init__(self, cfg=None):
        """
        We can pass a connection string, a **Flask** application object
        with the appropriate configuration, or nothing, in which
        case we will try to infer the correct database from
        the SPARROW_BACKEND_CONFIG file, if available.
        """
        self.config = None
        self.app = None
        if cfg is None:
            from ..app import App
            # Set config from environment variable
            cfg = App(__name__)
        if hasattr(cfg,'config'):
            self.app = cfg
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

        # Scoped session for database
        # https://docs.sqlalchemy.org/en/13/orm/contextual.html#unitofwork-contextual
        # https://docs.sqlalchemy.org/en/13/orm/session_basics.html#session-faq-whentocreate
        self.__session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.__session_factory)
        # Use the self.session_scope function to more explicitly manage sessions.

        # Automapping of database tables
        self.automap_base = None
        self.__models__ = None
        self.__tables__ = None
        self.__inspector__ = None
        self.automap_error = None
        # We're having trouble lazily automapping
        try:
            self.automap()
        except Exception as err:
            echo("Could not automap at database initialization", err=True)
            # TODO: We should raise this error, and find another way to
            # test if we've initialized the database yet.
            self.automap_error = err

    @contextmanager
    def session_scope():
        """Provide a transactional scope around a series of operations."""
        session = self.__session_factory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def exec_sql(self, fn):
        secho(Path(fn).name, fg='cyan', bold=True)
        run_sql_file(self.session, str(fn))

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
        Base.db = self

        # This stuff should be placed outside of core (one likely extension point).
        reflection_kwargs = dict(
            name_for_scalar_relationship=name_for_scalar_relationship,
            classname_for_table=_classname_for_table)

        Base.prepare(self.engine, reflect=True, **reflection_kwargs)
        for schema in ('vocabulary', 'core_view'):
            # Reflect tables in schemas we care about
            # Note: this will not reflect views because they don't have
            # primary keys.
            Base.metadata.reflect(
                    bind=self.engine,
                    schema=schema,
                    **reflection_kwargs)

        self.automap_base = Base
        # Database models we have extended with our own functions
        # (we need to add these to the automapped classes since they are not
        #  included by default)

        self.__models__ = ModelCollection(self.automap_base.classes)
        self.__tables__ = TableCollection(self.__models__)
        self.__models__.register(User, Project, Session)

        # Register a new class
        # Automap the core_view.datum relationship
        cls = self.automap_view("datum",
            Column("datum_id", Integer, primary_key=True),
            Column("analysis_id", Integer, ForeignKey(self.__tables__.analysis.c.id)),
            Column("session_id", Integer, ForeignKey(self.__tables__.session.c.id)),
            schema='core_view')
        self.__models__.register(cls)

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
            self.exec_sql(fn)

        try:
            self.app.run_hook('core-tables-initialized', self)
        except AttributeError as err:
            secho("Could not load plugins", fg='red', dim=True)
