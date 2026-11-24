import collections.abc
from datetime import datetime
from pathlib import Path
from time import perf_counter

from click import secho
from macrostrat.database import Database as BaseDatabase
from macrostrat.database import on_conflict
from macrostrat.database.mapper.utils import classname_for_table
from macrostrat.database.utils import run_sql
from macrostrat.utils import relative_path
from marshmallow import EXCLUDE, RAISE
from marshmallow.exceptions import ValidationError
from psycopg.types.datetime import TimestampLoader
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from sparrow.defs import SparrowError
from sparrow.loader import ModelSchema, model_interface
from sparrow.logs import get_logger

from .mapper import SparrowDatabaseMapper
from .models import DatumType, Project, Session, User

log = get_logger(__name__)


class _InfiniteTimestampLoader(TimestampLoader):
    def load(self, data):
        if bytes(data) == b"infinity":
            return datetime.max
        if bytes(data) == b"-infinity":
            return datetime.min
        return super().load(data)


def _read_infinite_timestamps(dbapi_connection, connection_record):
    # A lab embargoes data indefinitely with an `infinity` date, which the
    # driver has no Python value for unless it is given one
    adapters = getattr(dbapi_connection, "adapters", None)
    if adapters is not None:
        adapters.register_loader("timestamp", _InfiniteTimestampLoader)


class DatabaseMappingError(SparrowError):
    """Raised when a problem occurs with finding a database model"""


class Database(BaseDatabase):
    def __init__(self, db_conn, app=None):
        # Batched inserts cannot be reconciled with ON CONFLICT DO NOTHING imports
        super().__init__(db_conn, use_insertmanyvalues=False)
        self.app = app
        event.listen(self.engine, "connect", _read_infinite_timestamps)

    def automap(self):
        log.info("Automapping the database")
        t0 = perf_counter()

        self.mapper = SparrowDatabaseMapper(self)

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
        t1 = perf_counter()
        log.info(f"Finished automapping database: {t1 - t0:.2f}s")

    def run_sql(self, fn, params=None, **kwargs):
        if not params:
            # Schema fixtures contain literal percent signs (e.g. in format() calls)
            kwargs.setdefault("has_server_binds", False)
        return super().run_sql(fn, params, **kwargs)

    def run_fixtures(self, fixtures, params=None, **kwargs):
        if not params:
            kwargs.setdefault("has_server_binds", False)
        return super().run_fixtures(fixtures, params, **kwargs)

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
            self.run_sql(fp)

        from .schema import initialize_schema

        if self.app is None:
            secho("No application; plugin schemas are not built", fg="red", dim=True)
        initialize_schema(self)
        self.reload_postgrest_cache()

    def recreate_views(self):
        views = ["06-views.sql", "07-postgrest-api.sql"]
        for view in views:
            fp = relative_path(__file__, "fixtures", view)
            self.run_sql(fp)
        self.reload_postgrest_cache()
        try:
            self.app.run_hook("finalize-database-schema", self)
        except AttributeError as err:
            secho("Could not load plugins", fg="red", dim=True)
            secho(str(err))

    def reload_postgrest_cache(self):
        # Reload the Postgrest schema cache
        msg = "Reloading PostgREST schema cache"
        secho(msg, bold=True)
        log.info(msg)
        self.run_sql("NOTIFY pgrst, 'reload schema'")

    def schema_app(self, **kwargs):
        """This database's schema, for the schema management tools"""
        from .schema import create_schema_app

        return create_schema_app(self, **kwargs)

    def update_schema(self, dry_run=True, apply=True):
        """Bring the schema up to date, rehearsing on a copy of it first."""
        from .migration import create_schema_clone
        from .schema import update_schema

        if dry_run:
            log.info("Rehearsing the schema update")
            with create_schema_clone(self.engine) as engine:
                clone = Database(engine.url, self.app)
                try:
                    update_schema(clone)
                finally:
                    clone.cleanup()
        if not apply:
            return
        log.info("Updating the schema")
        update_schema(self)
