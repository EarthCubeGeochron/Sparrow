
from flask import Flask

from .database import Database
from .encoders import JSONEncoder
from .api import APIv1

def construct_app(db):
    app = Flask(__name__)

    api = APIv1(db)

    api.build_route("datum", schema='core_view')
    api.build_route("analysis", schema='core_view')
    api.build_route("age_datum", schema='core_view')
    api.build_route("dz_sample", schema='method_data')
    api.build_route("ar_age", schema='method_data')

    app.register_blueprint(api.blueprint, url_prefix='/api/v1')
    app.config['RESTFUL_JSON'] = dict(cls=JSONEncoder)
    return app
