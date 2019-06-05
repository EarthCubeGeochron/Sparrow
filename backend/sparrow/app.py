
from click import echo, style, secho
from os import path, environ
from flask import Flask, send_from_directory
from sqlalchemy.engine.url import make_url
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import NoSuchTableError
from flask_graphql import GraphQLView

from .graph import build_schema
from .encoders import JSONEncoder
from .api import APIv1
from .auth import AuthAPI
from .web import web
from .util import relative_path

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

    @property
    def database(self):
        from .database import Database
        if self.db is not None: return self.db
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

def construct_app(config=None, minimal=False):
    # Should allow configuration of template path
    app = App(__name__, config=config,
            template_folder=relative_path(__file__, "templates"))

    from .database import Database

    db = Database(app)

    if minimal:
        return app, db

    # Manage JSON Web tokens
    jwt = JWTManager(app)
    # Setup API
    api = APIv1(db)

    api.build_route("datum", schema='core_view')
    api.build_route("analysis", schema='core_view')
    api.build_route("session", schema='core_view')
    api.build_route("age_datum", schema='core_view')
    api.build_route("sample", schema='core_view')
    api.build_route("sample_data", schema='core_view')
    api.build_route("project", schema='core_view')
    api.build_route("material", schema='core_view')

    api.add_resource(AuthAPI, "/auth")

    try:
        api.build_route("aggregate_histogram", schema='lab_view')
    except NoSuchTableError:
        pass
    #api.build_route("ar_age", schema='method_data')

    app.api = api
    app.register_blueprint(api.blueprint, url_prefix='/api/v1')
    app.config['RESTFUL_JSON'] = dict(cls=JSONEncoder)

    app.register_blueprint(web, url_prefix='/')

    app.setup_graphql()

    # If we're serving on a low-key webserver and we
    # want to just serve assets without a file server...
    assets = app.config.get("ASSETS_DIRECTORY", None)
    if assets is not None:
        @app.route('/assets/<path:filename>')
        def assets_route(filename):
            return send_from_directory(assets, filename)

    return app, db
