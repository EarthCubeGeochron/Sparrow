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
from ..startup import wait_for_database, tables_exist

log = get_logger(__name__)


async def http_exception(request, exc):
    return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)


class Sparrow(Starlette):
    api_loaded: bool = False
    is_loaded: bool = False
    verbose: bool = False
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

    def bootstrap(self, init=True):
        self.setup_database(init=init)
        log.info("Booting up application server")
        self.setup_server()

    def setup_database(self, init=True):
        from ..database import Database

        wait_for_database(self.__db_url)
        _exists = tables_exist(self.__db_url)
        if init and not _exists:
            log.info("Creating database tables")
            db = Database(self.__db_url, self)
            db.initialize()
        elif init and _exists:
            log.info("Application tables exist")
        elif not _exists:
            log.warning("Database tables not found")

        self.db = Database(self.__db_url, self)
        self.run_hook("database-available", self.db)
        # Database is only "ready" when it is mapped
        if self.db.automap_base is None:
            self.database.automap()
        if self.db.automap_base is not None:
            self.run_hook("database-ready", self.db)
            self.database_ready = True
        return self.db

    def run_hook(self, *args, **kwargs):
        return self.plugins.run_hook(*args, **kwargs)

    @property
    def database(self):
        if self.db is None:
            self.setup_database(init=False)
        return self.db

    def initialize_plugins(self):
        if self.is_loaded:
            return
        self.plugins = prepare_plugin_manager(self)
        self.is_loaded = True
        log.info("Finished loading plugins")

    def setup_server(self):
        # This could maybe be added to the API...
        self.add_exception_handler(WebargsHTTPException, http_exception)

        if self.api_loaded:
            return
        route_table = []
        self.run_hook("add-routes", route_table)
        self.mount("/", Router(route_table))
        self.run_hook("finalize-routes")
        self.run_hook("asgi-setup", self)
        self.api_loaded = True
        log.info("Finished setting up server")
