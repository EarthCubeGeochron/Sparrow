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
from asgiref.wsgi import WsgiToAsgi
from .flask import App
from ..context import _setup_context
from ..api import APIv2
from ..api.v1 import APIv1
from ..plugins import SparrowPluginManager, SparrowPlugin, SparrowCorePlugin
from ..interface import InterfacePlugin
from ..auth import AuthPlugin
from ..ext.pychron import PyChronImportPlugin
from ..web import WebPlugin
from ..logs import get_logger
from ..encoders import JSONEncoder

log = get_logger(__name__)
# Should restructure using Starlette's config management
# https://www.starlette.io/config/

# Customize Sparrow's root logger so we don't get overridden by uvicorn
# We may want to customize this further eventually
# https://github.com/encode/uvicorn/issues/410

# Shim redirect for root path.
# TODO: clean this up


async def redirect(*args):
    return RedirectResponse("/api/v2/")


async def http_exception(request, exc):
    return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)


class Sparrow(Starlette):
    plugins: SparrowPluginManager
    flask: App
    api_loaded: bool = False
    is_loaded: bool = False
    verbose: bool = False
    db = None

    def __init__(self, *args, **kwargs):
        log.debug("Beginning app load")
        self.verbose = kwargs.pop("verbose", self.verbose)

        self.plugins = SparrowPluginManager()

        flask = App(
            self, __name__, config=kwargs.pop("config", None), verbose=self.verbose
        )
        self.flask = flask
        _setup_context(flask)

        start = kwargs.pop("start", False)

        super().__init__(*args, **kwargs)

        self.load()

        # This could maybe be added to the API...
        self.add_exception_handler(WebargsHTTPException, http_exception)

        log.debug("Finished app initialization")

        if start:
            log.debug("Starting application")
            self.load_phase_2()

    def setup_database(self, db=None):
        # This bootstrapping order leaves much to be desired
        from ..database import Database

        self.load()
        if self.db is not None and self.database_ready:
            return self.db
        if db is None:
            db = Database(self.flask)
        self.db = db
        self.run_hook("database-available", db)
        # Database is only "ready" when it is mapped
        if self.db.automap_base is not None:
            self.run_hook("database-ready", db)
            self.database_ready = True
        return db

    @property
    def database(self):
        if self.db is None:
            self.setup_database()
        return self.db

    def register_plugin(self, plugin):
        try:
            self.plugins.add(plugin)
        except Exception as err:
            name = plugin.__class__.__name__
            log.error("Could not register plugin", name, err)

    def __loaded(self):
        log.info("Initializing plugins")
        self.is_loaded = True
        self.plugins.finalize(self.flask)

    def run_hook(self, hook_name, *args, **kwargs):
        log.info("Running hook " + hook_name)
        method_name = "on_" + hook_name.replace("-", "_")
        for plugin in self.plugins:
            method = getattr(plugin, method_name, None)
            if method is None:
                continue
            method(*args, **kwargs)
            log.info("  plugin: " + plugin.name)

    def register_module_plugins(self, module):
        for _, obj in module.__dict__.items():
            try:
                assert issubclass(obj, SparrowPlugin)
            except (TypeError, AssertionError):
                continue

            if obj in [SparrowPlugin, SparrowCorePlugin]:
                continue

            self.register_plugin(obj)

    def load(self):
        if self.is_loaded:
            return
        import core_plugins

        self.register_plugin(AuthPlugin)
        # GraphQL is disabled for now
        # self.register_plugin(GraphQLPlugin)
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

        self.__loaded()

    def create_api(self):
        api_v2 = APIv2(self.flask)

        router = Router(
            [
                Route("/api/v2", endpoint=redirect),
                Mount("/api/v2/", app=api_v2),
                Mount("/", app=WsgiToAsgi(self.flask)),
            ]
        )

        self.mount("/", router)

        self.run_hook("asgi-setup", self)

    def load_phase_2(self):
        if self.api_loaded:
            return True

        # Database setup is likely redundant, but moves any database-mapping
        # errors forward.
        from ..database import Database

        db = self.setup_database(Database(self.flask))

        # Setup API
        api = APIv1(db)

        # Register all views in schema
        for tbl in db.entity_names(schema="core_view"):
            if tbl.endswith("_tree"):
                continue
            api.build_route(tbl, schema="core_view")

        for tbl in db.entity_names(schema="lab_view"):
            api.build_route(tbl, schema="lab_view")

        self.api = api
        self.flask.register_blueprint(api.blueprint, url_prefix="/api/v1")
        self.flask.config["RESTFUL_JSON"] = dict(cls=JSONEncoder)

        self.run_hook("api-initialized", api)
        self.run_hook("finalize-routes")

        # If we want to just serve assets without a file server...
        assets = self.flask.config.get("ASSETS_DIRECTORY", None)
        if assets is not None:

            @self.flask.route("/assets/<path:filename>")
            def assets_route(filename):
                return send_from_directory(assets, filename)

        self.api_loaded = True
        self.run_hook("load-complete")

        self.create_api()
