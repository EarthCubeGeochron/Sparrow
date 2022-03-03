"""
This module houses a
modern application server that translates our primary Sparrow app
(Flask/WSGI) to starlette (ASGI). This is for forward compatibility
with new async server architecture available in Python 3.6+.

This server's technology stack is similar to that of FastAPI,
but it uses the more mature Marshmallow schema-generation
package instead of FastAPI's Pydantic.
"""
from starlette.applications import Starlette
from starlette.routing import Router
from starlette.responses import JSONResponse
from webargs_starlette import WebargsHTTPException
from sparrow import settings
from ..logs import get_logger
from .plugins import prepare_plugin_manager, SparrowPluginManager
from ..database.util import wait_for_database
from ..startup import tables_exist

log = get_logger(__name__)


async def http_exception(request, exc):
    return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)


class Sparrow(Starlette):
    api_loaded: bool = False
    is_loaded: bool = False
    verbose: bool = False
    database_ready: bool = False
    __db_url: str
    db = None
    plugins: SparrowPluginManager

    def __init__(self, *args, **kwargs):
        log.debug("Beginning app load")
        self.verbose = kwargs.pop("verbose", self.verbose)
        self.__db_url = kwargs.pop("database", settings.DATABASE)
        self.config = kwargs.pop("config", None)
        self.initialize_plugins()

        super().__init__(*args, **kwargs)

    def bootstrap(self, init=False, force_db_setup=False, use_schema_cache=True):
        if init:
            self.init_database(force=force_db_setup)
        self.setup_database(use_cache=use_schema_cache)
        log.info("Booting up application server")
        self.setup_server()

    def __ensure_database(self):
        if self.db is not None:
            return
        from ..database import Database

        self.db = Database(self.__db_url, self)

    def init_database(self, drop=False, force=True):
        # This breaks everything for some reason
        wait_for_database(self.__db_url)
        _exists = tables_exist(self.__db_url)
        self.__ensure_database()
        if not _exists or drop or force:
            log.info("Creating database tables")
            self.db.initialize(drop=drop)
        elif _exists:
            log.info("Application tables exist")

    def setup_database(self, automap=True, use_cache=True):
        # If we set up the database twice, bad things will happen
        # with overriding of models, etc. We must make sure we only
        # set up the database once.
        self.__ensure_database()
        if self.database_ready:
            return self.db
        self.run_hook("database-available", self.db)
        # Database is only "ready" when it is mapped
        if self.db.mapper is None and automap:
            self.database.automap(use_cache=use_cache)
        if self.db.mapper is not None:
            self.run_hook("database-ready", self.db)
            self.database_ready = True
        return self.db

    def run_hook(self, *args, **kwargs):
        return self.plugins.run_hook(*args, **kwargs)

    @property
    def database(self):
        if self.db is None:
            self.setup_database()
        return self.db

    def initialize_plugins(self):
        if self.is_loaded:
            return
        self.plugins = prepare_plugin_manager(self)
        self.is_loaded = True
        log.info("Finished loading plugins")
        self.run_hook("plugins-initialized")

    def setup_server(self):
        # This could maybe be added to the API...
        log.info("Setting up server")
        self.add_exception_handler(WebargsHTTPException, http_exception)

        if self.api_loaded:
            return
        self.setup_database()
        route_table = []
        self.run_hook("add-routes", route_table)
        self.mount("/", Router(route_table))
        self.run_hook("finalize-routes")
        self.run_hook("asgi-setup", self)
        self.api_loaded = True
        log.info("Finished setting up server")
