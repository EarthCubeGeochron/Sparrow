from flama import Flama
from flama.responses import APIResponse
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


# Monkey-patch Flama's API response
APIResponse.render = render_json_response


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
        schema = iface()
        name = classname_for_table(schema.opts.model.__table__)
        log.info(str(name))

        def list_items():
            schema = iface()
            res = db.session.query(schema.opts.model).limit(100).all()
            return [schema.dump(r) for r in res]

        self.add_route("/" + name, list_items, methods=["GET"])
