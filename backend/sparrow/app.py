from click import echo, style, secho
from os import environ
from flask import Flask, send_from_directory
from sqlalchemy.engine.url import make_url
import logging

from .encoders import JSONEncoder
from .api import APIv1
from .util import relative_path
from .plugins import SparrowPluginManager, SparrowPlugin, SparrowCorePlugin
from .interface import InterfacePlugin
from .auth import AuthPlugin
#from .graph import GraphQLPlugin
from .web import WebPlugin

def echo_error(message, obj=None, err=None):
    if obj is not None:
        message += " "+style(str(obj), bold=True)
    secho(message, fg='red', err=True)
    if err is not None:
        secho("  "+str(err), fg='red', err=True)


class App(Flask):
    def __init__(self, *args, **kwargs):
        # Setup config as suggested in http://flask.pocoo.org/docs/1.0/config/
        cfg = kwargs.pop("config", None)
        verbose = kwargs.pop("verbose", True)
        super().__init__(*args, **kwargs)
        self.verbose = verbose

        self.config.from_object('sparrow.default_config')
        if cfg is None:
            cfg = environ.get("SPARROW_BACKEND_CONFIG", None)
        try:
            self.config.from_pyfile(cfg)
        except RuntimeError as err:
            secho("No lab-specific configuration file found.", bold=True)
            print(str(err))

        self.db = None
        dburl = self.config.get("DATABASE")
        self.db_url = make_url(dburl)
        self.dbname = self.db_url.database

        self.plugins = SparrowPluginManager()

    def echo(self, msg):
        if not self.verbose:
            return
        echo(msg, err=True)

    @property
    def database(self):
        from .database import Database
        if self.db is not None:
            return self.db
        self.db = Database(self)
        return self.db

    def register_plugin(self, plugin):
        try:
            self.plugins.add(plugin)
        except Exception as err:
            name = plugin.__class__.__name__
            echo_error("Could not register plugin", name, err)


    def loaded(self):
        self.echo("Initializing plugins")
        self.plugins.finalize(self)

    def run_hook(self, hook_name, *args, **kwargs):
        self.echo("Running hook "+hook_name)
        method_name = "on_"+hook_name.replace("-","_")
        for plugin in self.plugins:
            try:
                method = getattr(plugin, method_name)
                method(*args, **kwargs)
                self.echo("  plugin: "+plugin.name)
            except AttributeError as err:
                continue

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
        import sparrow_plugins
        import core_plugins
        self.register_plugin(AuthPlugin)
        # GraphQL is disabled for now
        # self.register_plugin(GraphQLPlugin)
        self.register_plugin(WebPlugin)
        self.register_plugin(InterfacePlugin)
        self.register_module_plugins(core_plugins)
        self.register_module_plugins(sparrow_plugins)
        self.loaded()


def construct_app(config=None, minimal=False, **kwargs):
    app = App(__name__, config=config,
              template_folder=relative_path(__file__, "templates"),
              **kwargs)

    app.load()

    from .database import Database

    db = Database(app)
    if db.automap_error is not None:
        return app, db
    if minimal:
        return app, db


    app.run_hook("database-ready")

    # Setup API
    api = APIv1(db)

    # Register all views in schema
    for tbl in db.entity_names(schema='core_view'):
        if tbl.endswith("_tree"):
            continue
        api.build_route(tbl, schema='core_view')

    for tbl in db.entity_names(schema='lab_view'):
        api.build_route(tbl, schema='lab_view')

    app.api = api
    app.register_blueprint(api.blueprint, url_prefix='/api/v1')
    app.config['RESTFUL_JSON'] = dict(cls=JSONEncoder)

    app.run_hook("api-initialized", api)
    app.run_hook("finalize-routes")

    # If we want to just serve assets without a file server...
    assets = app.config.get("ASSETS_DIRECTORY", None)
    if assets is not None:
        @app.route('/assets/<path:filename>')
        def assets_route(filename):
            return send_from_directory(assets, filename)

    return app, db
