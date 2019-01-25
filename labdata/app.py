
from os import path
from flask import Flask

from .database import Database
from .encoders import JSONEncoder
from .api import APIv1
from .web import web
from .util import relative_path

def construct_app(db):
    # Should allow configuration of template path
    app = Flask(__name__,
            template_folder=relative_path(__file__, "templates"))

    api = APIv1(db)

    api.build_route("datum", schema='core_view')
    api.build_route("analysis", schema='core_view')
    api.build_route("age_datum", schema='core_view')
    api.build_route("sample", schema='core_view')
    api.build_route("project", schema='core_view')

    api.build_route("dz_sample", schema='method_data')
    api.build_route("ar_age", schema='method_data')

    app.api = api
    app.register_blueprint(api.blueprint, url_prefix='/api/v1')
    app.config['RESTFUL_JSON'] = dict(cls=JSONEncoder)

    app.register_blueprint(web, url_prefix='/')

    return app
