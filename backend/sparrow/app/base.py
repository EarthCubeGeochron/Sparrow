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
from starlette.routing import Mount, Route, RedirectResponse, Router
from starlette.responses import JSONResponse
from webargs_starlette import WebargsHTTPException
from sparrow import settings
from ..context import _setup_context
from ..api import APIv2Plugin
from ..legacy.api_v1 import APIv1Plugin
from ..plugins import (
    SparrowPluginManager,
    SparrowPlugin,
    SparrowCorePlugin,
)
from ..interface import InterfacePlugin
from ..auth import AuthPlugin
from ..ext.pychron import PyChronImportPlugin
from ..web import WebPlugin
from ..logs import get_logger

log = get_logger(__name__)


async def http_exception(request, exc):
    return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)


class Sparrow(Starlette):
    plugins: SparrowPluginManager
    api_loaded: bool = False
    is_loaded: bool = False
    verbose: bool = False
    db = None

    def __init__(self, *args, **kwargs):
        log.debug("Beginning app load")
        self.verbose = kwargs.pop("verbose", self.verbose)

        self.config = kwargs.pop("config", None)
        self.plugins = SparrowPluginManager()

        _setup_context(self)

        start = kwargs.pop("start", False)

        super().__init__(*args, **kwargs)

        self.initialize_plugins()

        # This could maybe be added to the API...
        self.add_exception_handler(WebargsHTTPException, http_exception)

        if start:
            log.debug("Starting application")
            self.setup_server()

    def setup_database(self):
        from ..database import Database

        self.db = Database(settings.DATABASE, self)
        self.run_hook("database-available", self.db)
        # Database is only "ready" when it is mapped
        if self.db.automap_base is not None:
            self.run_hook("database-ready", self.db)
            self.database_ready = True
        return self.db

    @property
    def database(self):
        if self.db is None:
            self.setup_database()
        return self.db

    def register_plugin(self, plugin):
        try:
            self.plugins.add(plugin)
        except Exception as err:
            log.error("Could not register plugin", plugin.name, err)

    def run_hook(self, hook_name, *args, **kwargs):
        log.info("Running hook " + hook_name)
        method_name = "on_" + hook_name.replace("-", "_")
        for plugin in self.plugins:
            method = getattr(plugin, method_name, None)
            if method is None:
                continue
            log.info("  plugin: " + plugin.name)
            method(*args, **kwargs)

    def register_module_plugins(self, module):
        for _, obj in module.__dict__.items():
            try:
                assert issubclass(obj, SparrowPlugin)
            except (TypeError, AssertionError):
                continue

            if obj in [SparrowPlugin, SparrowCorePlugin]:
                continue

            self.register_plugin(obj)

    def initialize_plugins(self):
        if self.is_loaded:
            return
        import core_plugins

        self.register_plugin(AuthPlugin)
        # GraphQL is disabled for now
        # self.register_plugin(GraphQLPlugin)
        self.register_plugin(APIv1Plugin)
        self.register_plugin(APIv2Plugin)
        self.register_plugin(WebPlugin)
        self.register_plugin(InterfacePlugin)
        self.register_plugin(PyChronImportPlugin)
        self.register_module_plugins(core_plugins)

        # Try to import external plugins, but they might not be defined.
        try:
            import sparrow_plugins

            self.register_module_plugins(sparrow_plugins)
        except ModuleNotFoundError as err:
            log.info("Could not find external Sparrow plugins.")
            log.info(err)

        self.is_loaded = True
        self.plugins.finalize(self)
        log.info("Finished loading plugins")

    def setup_server(self):
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
