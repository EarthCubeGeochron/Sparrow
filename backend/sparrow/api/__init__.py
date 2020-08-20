from flama.exceptions import SerializationError, ValidationError
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from sparrow.logs import get_logger
from json import dumps
from ..database.mapper.util import classname_for_table
from ..encoders import JSONEncoder
from typing import Any
from webargs_starlette import parser
from webargs.fields import DelimitedList, Str, Int
from sqlakeyset import get_page
from marshmallow_sqlalchemy.fields import get_primary_keys
from sqlalchemy import desc
from json.decoder import JSONDecodeError
from .schema import schema

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


async def http_exception(request, exc):
    return JSONResponse(
        {"error": {"detail": exc.detail, "status_code": exc.status_code}},
        status_code=exc.status_code,
    )


exception_handlers = {HTTPException: http_exception}


class APIResponse(JSONResponse):
    # copied from https://github.com/perdy/flama/blob/master/flama/responses.py
    media_type = "application/json"

    def __init__(self, schema=None, *args, **kwargs):
        self.schema = schema
        super().__init__(*args, **kwargs)

    def render(self, content: Any):
        # Use output schema to validate and format data

        paging = getattr(content, "paging", None)
        page = {}
        if paging is not None:
            page["next_page"] = paging.bookmark_next if paging.has_next else None
            page["previous_page"] = (
                paging.bookmark_previous if paging.has_previous else None
            )

        try:
            if self.schema is not None:
                content = self.schema.dump(content)
        except Exception:
            raise SerializationError(status_code=500)

        if not content:
            return b""

        return super().render(dict(data=content, **page))


class APIEntry(HTTPEndpoint):
    async def get(self, request):
        """
        description:
            A test API base route.
        responses:
            200:
                description: It's alive!
        """
        desc = {d["route"]: d["description"] for d in request.app.route_descriptions}
        return JSONResponse({"routes": desc})


class APIv2(Starlette):
    def __init__(self, app):
        self._app = app
        self.route_descriptions = []
        api_args = dict(
            title="Sparrow API",
            version="2.0",
            description="An API for accessing geochemical data",
        )
        super().__init__(exception_handlers=exception_handlers)
        self._add_routes()

    def _add_routes(self):

        self.add_route("/", APIEntry)

        db = self._app.database

        for iface in db.interface:
            self._add_schema_route(iface)

        self.add_route("/schema", schema, methods=["GET"], include_in_schema=False)

    def _add_schema_route(self, iface):
        db = self._app.database
        schema = iface(many=True)
        name = classname_for_table(schema.opts.model.__table__)
        log.info(str(name))

        args_schema = {
            "nest": DelimitedList(Str(), missing=[]),
            "page": Str(missing=None),
            "per_page": Int(missing=20),
        }

        # Flama's API methods know to deserialize this with the proper model
        async def list_items(request):
            log.info(request)
            args = await parser.parse(args_schema, request, location="querystring")
            log.info(args)

            schema = iface(many=True, allowed_nests=args["nest"])

            # By default, we order by the "natural" order of Primary Keys. This
            # is not really what we want in most cases, probably.
            pk = [desc(p) for p in get_primary_keys(schema.opts.model)]
            q = db.session.query(schema.opts.model).order_by(*pk)
            # https://github.com/djrobstep/sqlakeyset
            try:
                res = get_page(q, per_page=args["per_page"], page=args["page"])
            except ValueError:
                raise ValidationError("Invalid page token.")

            return APIResponse(schema, res)

        endpoint = "/" + name
        self.add_route(endpoint, list_items, methods=["GET"])

        async def filter_items(request):
            """Shim route to filter models. May not want to include this in the
            final design, but it is valuable for testing."""
            try:
                res = await request.json()
            except JSONDecodeError:
                raise ValidationError("Expected a GET or POST body for filter.")

            return JSONResponse(res)

        # self.add_route(endpoint + "/filter", filter_items, methods=["GET", "POST"])

        tbl = schema.opts.model.__table__
        basic_info = dict(
            route=endpoint, table=tbl.name, schema=tbl.schema, description="A route!",
        )
        self.route_descriptions.append(basic_info)
