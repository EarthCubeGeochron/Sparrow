from pathlib import Path
from click import secho
from time import perf_counter

from sqlalchemy.schema import ForeignKey, Column
from sqlalchemy.types import Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from marshmallow.exceptions import ValidationError
from marshmallow import RAISE, EXCLUDE
from macrostrat.database import Database as BaseDatabase
from macrostrat.database import on_conflict
from macrostrat.database.utils import run_sql
import collections.abc

from .models import User, Project, Session, DatumType
from sparrow.logs import get_logger
from macrostrat.utils import relative_path
from sparrow.loader import ModelSchema, model_interface
from sparrow.defs import SparrowError
from .migration import SparrowDatabaseMigrator
from .mapper import SparrowDatabaseMapper
from macrostrat.database.mapper.utils import classname_for_table

log = get_logger(__name__)


class DatabaseMappingError(SparrowError):
    """Raised when a problem occurs with finding a database model"""


class Database(BaseDatabase):
    def __init__(self, db_conn, app=None):
        super().__init__(db_conn)
        self.app = app

    def automap(self, use_cache=True):
        log.info("Automapping the database")
        t0 = perf_counter()

        self.mapper = SparrowDatabaseMapper(self, use_cache=use_cache)

        # Database models we have extended with our own functions
        # (we need to add these to the automapped classes since
        #  they are not included by default)
        # TODO: there is probably a way to do this without having to
        # manually register the models
        log.info("Registering model overrides")
        self.mapper.register_models(User, Project, Session, DatumType)

        # Register a new class
        # Automap the core_view.datum relationship
        cls = self.mapper.automap_view(
            "datum",
            Column("datum_id", Integer, primary_key=True),
            Column("analysis_id", Integer, ForeignKey(self.table.analysis.c.id)),
            Column("session_id", Integer, ForeignKey(self.table.session.c.id)),
            schema="core_view",
        )
        self.mapper.register_models(cls)
        if self.app:
            self.app.run_hook("database-mapped")
        if not use_cache:
            self.mapper._cache_database_map()
        t1 = perf_counter()
        log.info(f"Finished automapping database: {t1-t0:.2f}s")

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

    def load_data(self, model_name, data, session=None, **kwargs):
        """Load data into the database using a schema-based importing tool.

        kwargs:
            - session: the session to use for the import
            - strict: if True, will raise an exception on extra fields
            - unknown: Pass through to Marshmallow's load() behavior on unknown fields
            - many: whether we should attempt to load multiple objects (default: if input is a list)
        """
        if session is None:
            session = self.session
        # Do an end-around for lack of creating interfaces on app startup
        model = getattr(self.model, model_name)

        # Check if we want to load a list of instances
        many = isinstance(data, collections.abc.Sequence) and not isinstance(data, str)
        many = kwargs.pop("many", many)

        many = isinstance(data, list)
        if not hasattr(model, "__mapper__"):
            raise DatabaseMappingError(
                f"Model {model} does not have appropriate field mapping"
            )
        schema = model_interface(model, session)(many=many)

        strict_mode = kwargs.pop("strict", False)
        default_unknown = RAISE if strict_mode else EXCLUDE

        unknown = kwargs.pop("unknown", default_unknown)

        with on_conflict("do-nothing"):
            try:
                log.info(f"Initiating load of {model_name}")
                res = schema.load(data, session=session, unknown=unknown, **kwargs)
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

    def initialize(self, drop=False, quiet=False):
        log.info("Initializing database")
        secho("Creating core schema...", bold=True)

        if drop:
            fp = relative_path(__file__, "procedures", "drop-all-tables.sql")
            self.exec_sql(fp)

        p = Path(relative_path(__file__, "fixtures"))
        filenames = list(p.glob("*.sql"))
        filenames.sort()

        for _fn in filenames:
            self.exec_sql(_fn)

        # Reload the Postgrest schema cache
        msg = "Reloading PostgREST schema cache"
        secho(msg, bold=True)
        log.info(msg)
        self.engine.execute("NOTIFY pgrst, 'reload schema'")

        try:
            self.app.run_hook("core-tables-initialized", self)
            self.app.run_hook("finalize-database-schema", self)
        except AttributeError as err:
            secho("Could not load plugins", fg="red", dim=True)
            secho(str(err))

    def update_schema(self, **kwargs):
        # Might be worth creating an interactive upgrader
        from sparrow import migrations

        migrator = SparrowDatabaseMigrator(self)
        migrator.add_module(migrations)
        self.app.run_hook("prepare-database-migrations", migrator)
        # TODO: deprecate this hook
        self.app.run_hook("prepare-database-upgrade", migrator)
        migrator.run_migration(**kwargs)
