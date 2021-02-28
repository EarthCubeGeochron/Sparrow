from contextlib import contextmanager
from pathlib import Path
from click import secho

from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.schema import ForeignKey, Column
from sqlalchemy.types import Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from marshmallow.exceptions import ValidationError

from .util import run_sql_file, run_query, get_or_create
from .models import User, Project, Session, DatumType
from .mapper import MappedDatabaseMixin
from ..logs import get_logger
from ..util import relative_path
from ..interface import ModelSchema, model_interface
from ..exceptions import DatabaseMappingError
from .postgresql import on_conflict
from .migration import SparrowDatabaseMigrator

metadata = MetaData()

log = get_logger(__name__)


class Database(MappedDatabaseMixin):
    def __init__(self, db_conn, app=None):
        """
        We can pass a connection string, a **Flask** application object
        with the appropriate configuration, or nothing, in which
        case we will try to infer the correct database from
        the SPARROW_BACKEND_CONFIG file, if available.
        """
        log.info(f"Setting up database connection '{db_conn}'")
        self.engine = create_engine(db_conn, executemany_mode="batch")
        metadata.create_all(bind=self.engine)
        self.meta = metadata
        self.app = app

        # Scoped session for database
        # https://docs.sqlalchemy.org/en/13/orm/contextual.html#unitofwork-contextual
        # https://docs.sqlalchemy.org/en/13/orm/session_basics.html#session-faq-whentocreate
        self._session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self._session_factory)
        # Use the self.session_scope function to more explicitly manage sessions.

    def automap(self):
        log.info("Automapping the database")
        super().automap()
        # Database models we have extended with our own functions
        # (we need to add these to the automapped classes since
        #  they are not included by default)
        # TODO: there is probably a way to do this without having to
        # manually register the models
        self.register_models(User, Project, Session, DatumType)
        # Register a new class
        # Automap the core_view.datum relationship
        cls = self.automap_view(
            "datum",
            Column("datum_id", Integer, primary_key=True),
            Column("analysis_id", Integer, ForeignKey(self.table.analysis.c.id)),
            Column("session_id", Integer, ForeignKey(self.table.session.c.id)),
            schema="core_view",
        )
        self.register_models(cls)
        self.app.run_hook("database-mapped")

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        self.__old_session = self.session
        session = self._session_factory()
        self.session = session
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            self.session = self.__old_session

    def model_schema(self, model_name) -> ModelSchema:
        """
        Create a SQLAlchemy instance from data conforming to an import schema
        """
        try:
            iface = getattr(self.interface, model_name)
            return iface()
        except AttributeError as err:
            raise DatabaseMappingError(
                f"Could not find schema interface for model '{model_name}'"
            )

    def _flush_nested_objects(self, session):
        """
        Flush objects remaining in a session (generally these are objects loaded
        during schema-based importing).
        """
        for object in session:
            try:
                session.flush(objects=[object])
                log.debug(f"Successfully flushed instance {object}")
            except IntegrityError as err:
                session.rollback()
                log.debug(err)

    def load_data(self, model_name, data, session=None, **kwargs):
        """Load data into the database using a schema-based importing tool"""
        if session is None:
            session = self.session
        # Do an end-around for lack of creating interfaces on app startup
        model = getattr(self.model, model_name)
        if not hasattr(model, "__mapper__"):
            raise DatabaseMappingError(
                f"Model {model} does not have appropriate field mapping"
            )
        schema = model_interface(model, session)()

        with on_conflict("do-nothing"):
            try:
                log.info(f"Initiating load of {model_name}")
                res = schema.load(data, session=session, **kwargs)
                log.info("Entering final commit phase of import")
                log.info(f"Adding top-level object {res}")
                session.add(res)
                log.info("Committing entire transaction")
                session.commit()
                return res
            except (IntegrityError, ValidationError, FlushError) as err:
                session.rollback()
                log.debug(err)
                raise err

    def get_existing_instance(self, model_name, filter_params):
        schema = self.model_schema(model_name)
        return schema.load(filter_params, session=self.session)

    def get_instance(self, model_name, filter_params):
        schema = self.model_schema(model_name)
        res = schema.load(filter_params, session=self.session, partial=True)
        return res

    def exec_sql(self, fn):
        # TODO: refactor this to exec_sql_file
        secho(Path(fn).name, fg="cyan", bold=True)
        run_sql_file(self.session, str(fn))

    def exec_query(self, *args):
        run_query(self.session, *args)

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

    def get(self, model, *args, **kwargs):
        if isinstance(model, str):
            model = getattr(self.model, model)
        return self.session.query(model).get(*args, **kwargs)

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

        for fn in filenames:
            self.exec_sql(fn)

        try:
            self.app.run_hook("core-tables-initialized", self)
        except AttributeError as err:
            secho("Could not load plugins", fg="red", dim=True)
            secho(str(err))

    def update_schema(self, check=True):
        # Might be worth creating an interactive upgrader
        from sparrow import migrations

        migrator = SparrowDatabaseMigrator(self)
        migrator.add_module(migrations)
        self.app.run_hook("prepare-database-upgrade", migrator)
        migrator.run_migration(dry_run=True)