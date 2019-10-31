from click import echo, style, secho
from os import path, environ
from flask import Flask, send_from_directory
from sqlalchemy import inspect
from sqlalchemy.engine.url import make_url
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import NoSuchTableError
from flask_graphql import GraphQLView
from toposort import toposort_flatten

from .graph import build_schema
from .encoders import JSONEncoder
from .api import APIv1
from .auth import AuthAPI
from .web import web
from .util import relative_path
from .plugins import SparrowCorePlugin, SparrowPluginManager


class App(Flask):
    def __init__(self, *args, **kwargs):
        # Setup config as suggested in http://flask.pocoo.org/docs/1.0/config/
        cfg = kwargs.pop("config", None)
        super().__init__(*args, **kwargs)

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

    @property
    def database(self):
        from .database import Database
        if self.db is not None:
            return self.db
        self.db = Database(self)
        return self.db

    def setup_graphql(self):
        ctx = dict(session=self.database.session)
        s = build_schema(self.database)
        view_func = GraphQLView.as_view('graphql',
                                        schema=s,
                                        graphiql=True,
                                        context=ctx)

        self.add_url_rule('/graphql', view_func=view_func)

    def register_plugin(self, plugin):
        self.plugins.add(plugin)

    def loaded(self):
        echo("Initializing plugins")
        self.plugins.finalize(self)

    def run_hook(self, hook_name, *args, **kwargs):
        echo("Running hook "+hook_name)
        method_name = "on_"+hook_name.replace("-","_")
        for plugin in self.plugins:
            try:
                method = getattr(plugin, method_name)
                echo("  plugin: "+plugin.name)
                method(*args, **kwargs)
            except AttributeError:
                continue


class AuthPlugin(SparrowCorePlugin):
    name = "auth-api"
    def on_api_initialized(self, api):
        api.add_resource(AuthAPI, "/auth")


def construct_app(config=None, minimal=False):
    app = App(__name__, config=config,
              template_folder=relative_path(__file__, "templates"))

    app.register_plugin(AuthPlugin)

    from .database import Database

    db = Database(app)
    if db.automap_error is not None:
        return app, db
    if minimal:
        return app, db

    app.loaded()

    app.run_hook("database-ready")

    # Manage JSON Web tokens
    JWTManager(app)
    # Setup API
    api = APIv1(db)

    app.run_hook("api-initialized", api)

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

    app.register_blueprint(web, url_prefix='/')

    app.setup_graphql()

    # If we want to just serve assets without a file server...
    assets = app.config.get("ASSETS_DIRECTORY", None)
    if assets is not None:
        @app.route('/assets/<path:filename>')
        def assets_route(filename):
            return send_from_directory(assets, filename)

    return app, db
