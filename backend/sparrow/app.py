from click import echo, style, secho
from os import environ
from flask import Flask, send_from_directory
from sqlalchemy.engine.url import make_url
import logging

from .encoders import JSONEncoder
from .api.v1 import APIv1
from .util import relative_path
from .plugins import SparrowPluginManager, SparrowPlugin, SparrowCorePlugin
from .interface import InterfacePlugin
from .auth import AuthPlugin

# from .graph import GraphQLPlugin
from .web import WebPlugin
from .logs import get_logger, console_handler

log = get_logger(__name__)


def echo_error(message, obj=None, err=None):
    if obj is not None:
        message += " " + style(str(obj), bold=True)
    log.error(message)
    if err is not None:
        log.error("  " + str(err))


class App(Flask):
    def __init__(self, *args, **kwargs):
        # Setup config as suggested in http://flask.pocoo.org/docs/1.0/config/
        cfg = kwargs.pop("config", None)
        verbose = kwargs.pop("verbose", True)
        super().__init__(*args, **kwargs)
        self.is_loaded = False
        self.api_loaded = False
        self.verbose = verbose

        self.config.from_object("sparrow.default_config")
        if cfg is None:
            cfg = environ.get("SPARROW_BACKEND_CONFIG", None)
        try:
            self.config.from_pyfile(cfg)
        except RuntimeError as err:
            log.info("No lab-specific configuration file found.")

        self.db = None
        dburl = self.config.get("DATABASE")
        self.db_url = make_url(dburl)
        self.dbname = self.db_url.database

        self.plugins = SparrowPluginManager()

    def echo(self, msg):
        if not self.verbose:
            return
        echo(msg, err=True)

    def setup_database(self, db=None):
        from .database import Database

        self.load()
        if self.db is not None:
            return self.db
        if db is None:
            db = Database(self)
        self.db = db
        self.run_hook("database-available")
        # Database is only "ready" when it is mapped
        if self.db.automap_base is not None:
            self.run_hook("database-ready")
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
            echo_error("Could not register plugin", name, err)

    def __loaded(self):
        log.info("Initializing plugins")
        self.is_loaded = True
        self.plugins.finalize(self)

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
        for name, obj in module.__dict__.items():
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
        self.register_module_plugins(core_plugins)

        # Try to import external plugins, but they might not be defined.
        try:
            import sparrow_plugins

            self.register_module_plugins(sparrow_plugins)
        except ModuleNotFoundError as err:
            log.error("Could not find external Sparrow plugins.")
            log.error(err)

        self.__loaded()

    def load_phase_2(self):
        if self.api_loaded:
            return True
        # Database setup is likely redundant, but moves any database-mapping
        # errors forward.
        from .database import Database

        db = self.setup_database(Database(self))

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
        self.register_blueprint(api.blueprint, url_prefix="/api/v1")
        self.config["RESTFUL_JSON"] = dict(cls=JSONEncoder)

        self.run_hook("api-initialized", api)
        self.run_hook("finalize-routes")

        # If we want to just serve assets without a file server...
        assets = self.config.get("ASSETS_DIRECTORY", None)
        if assets is not None:

            @self.route("/assets/<path:filename>")
            def assets_route(filename):
                return send_from_directory(assets, filename)

        self.api_loaded = True
