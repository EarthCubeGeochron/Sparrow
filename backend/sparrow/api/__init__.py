from flama.responses import APIResponse as BaseAPIResponse
from flama.exceptions import SerializationError
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from sparrow.logs import get_logger
from json import dumps
from ..database.mapper.util import classname_for_table
from ..encoders import JSONEncoder
from typing import Any
from webargs_starlette import parser
from webargs.fields import DelimitedList, Str
from sqlakeyset import get_page

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


class APIResponse(JSONResponse):
    # copied from https://github.com/perdy/flama/blob/master/flama/responses.py
    media_type = "application/json"

    def __init__(self, schema=None, *args, **kwargs):
        self.schema = schema
        super().__init__(*args, **kwargs)

    def render(self, content: Any):
        # Use output schema to validate and format data
        try:
            if self.schema is not None:
                content = self.schema.dump(content)
        except Exception:
            raise SerializationError(status_code=500)

        if not content:
            return b""

        return super().render(dict(data=content))


def hello_world():
    """
    description:
        A test API base route.
    responses:
        200:
            description: It's alive!
    """
    return {"Hello": "world!"}


class APIv2(Starlette):
    def __init__(self, app):
        self._app = app
        api_args = dict(
            title="Sparrow API",
            version="2.0",
            description="An API for accessing geochemical data",
        )
        super().__init__()
        self._add_routes()

    def _add_routes(self):
        self.add_route("/", hello_world, methods=["GET"])

        db = self._app.database

        for iface in db.interface:
            self._add_schema_route(iface)

    def _add_schema_route(self, iface):
        db = self._app.database
        schema = iface(many=True)
        name = classname_for_table(schema.opts.model.__table__)
        log.info(str(name))

        args_schema = {"nest": DelimitedList(Str(), missing=[])}

        # Flama's API methods know to deserialize this with the proper model
        async def list_items(request):
            args = await parser.parse(args_schema, request, location="querystring")
            log.info(args)

            schema = iface(many=True, allowed_nests=args["nest"])
            q = db.session.query(schema.opts.model)

            res = get_page(q, per_page=20)
            return APIResponse(schema, res)

        self.add_route("/" + name, list_items, methods=["GET"])
