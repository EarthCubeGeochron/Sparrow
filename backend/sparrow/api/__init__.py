from flama import Flama
from starlette.responses import JSONResponse
from sparrow.logs import get_logger
from json import dumps
from ..database.mapper.util import classname_for_table
from ..encoders import JSONEncoder
from typing import Any

log = get_logger(__name__)


def render_json_response(self, content: Any) -> bytes:
    """Shim for starlette's JSONResponse (subclassed by Flama)
    that properly encodes Decimal and geometries.
    """
    return dumps(
        content,
        ensure_ascii=False,
        allow_nan=False,
        indent=None,
        separators=(",", ":"),
        cls=JSONEncoder,
    ).encode("utf-8")


# Monkey-patch Starlette's API response
JSONResponse.render = render_json_response


def hello_world():
    """
    description:
        A test API base route.
    responses:
        200:
            description: It's alive!
    """
    return {"Hello": "world!"}


class APIv2(Flama):
    def __init__(self, app):
        self._app = app
        super().__init__(
            title="Sparrow API",
            version="2.0",
            description="An API for accessing geochemical data",
        )
        self._add_routes()

    def _add_routes(self):
        self.add_route("/", hello_world, methods=["GET"])

        db = self._app.database

        for iface in db.interface:
            self._add_schema_route(iface)

    def _add_schema_route(self, iface):
        db = self._app.database
        schema = iface(many=True, allowed_nests=["session", "analysis", "datum"])
        name = classname_for_table(schema.opts.model.__table__)
        log.info(str(name))

        # Flama's API methods know to deserialize this with the proper model
        def list_items() -> schema:
            return db.session.query(schema.opts.model).limit(100).all()

        self.add_route("/" + name, list_items, methods=["GET"])
