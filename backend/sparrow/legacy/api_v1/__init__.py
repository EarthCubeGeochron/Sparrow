from .util import APIResourceCollection
from .core import APIv1, ModelEditParser, get_jwt_identity
from ...plugins import SparrowCorePlugin
from ...encoders import JSONEncoder
from ._legacy_app import App
from starlette.routing import Mount
from asgiref.wsgi import WsgiToAsgi

# Setup API


class APIv1Plugin(SparrowCorePlugin):
    """A plugin that wraps Sparrow's legacy API"""

    name = "api-v1"
    sparrow_version = ">=2.*"

    def on_add_routes(self, route_table):
        db = self.app.database

        api = APIv1(db)

        # Register all views in schema
        for tbl in db.entity_names(schema="core_view"):
            if tbl.endswith("_tree"):
                continue
            api.build_route(tbl, schema="core_view")

        for tbl in db.entity_names(schema="lab_view"):
            api.build_route(tbl, schema="lab_view")

        self.api = api
        self._flask = App(self.app, __name__)
        self._flask.register_blueprint(api.blueprint, url_prefix="")
        self._flask.config["RESTFUL_JSON"] = dict(cls=JSONEncoder)
        route_table.append(Mount("/api/v1/", WsgiToAsgi(self._flask)))
        self.app.run_hook("api-v1-initialized", api)
