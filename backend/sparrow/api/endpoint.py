from flama.exceptions import SerializationError, ValidationError
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
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

log = get_logger(__name__)


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

        return self._encode(dict(data=content, **page))

    def _encode(self, content: Any) -> bytes:
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


class ModelAPIEndpoint(HTTPEndpoint):
    class Meta:
        database = None
        schema = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = self.Meta()
        for k in ("database", "schema"):
            if getattr(self.meta, k) is None:
                raise ValueError(
                    f"Meta value '{k}' must be provided for ModelAPIEndpoint"
                )

        schema = self.meta.schema
        name = classname_for_table(schema.opts.model.__table__)
        log.info(str(name))

        self.instance_schema = dict(nest=DelimitedList(Str(), missing=[]),)

        self.args_schema = dict(
            **self.instance_schema, page=Str(missing=None), per_page=Int(missing=20),
        )

    def query(self, schema):
        db = self.meta.database
        return db.session.query(schema.opts.model)

    async def get_single(self, request):
        """Handler for single instance GET requests"""
        args = await parser.parse(self.instance_schema, request, location="querystring")
        id = request.path_params.get("id")
        log.info(id, args)

        schema = self.meta.schema(many=False, allowed_nests=args["nest"])
        res = self.query(schema).get(id)
        # https://github.com/djrobstep/sqlakeyset
        return APIResponse(schema, res)

    async def get(self, request):
        """Handler for all GET requests"""

        if request.path_params.get("id") is not None:
            return await self.get_single(request)

        log.info(request)
        log.info(request.path_params)
        args = await parser.parse(self.args_schema, request, location="querystring")
        log.info(args)

        schema = self.meta.schema(many=True, allowed_nests=args["nest"])

        # By default, we order by the "natural" order of Primary Keys. This
        # is not really what we want in most cases, probably.
        pk = [desc(p) for p in get_primary_keys(schema.opts.model)]
        q = self.query(schema).order_by(*pk)
        # https://github.com/djrobstep/sqlakeyset
        try:
            res = get_page(q, per_page=args["per_page"], page=args["page"])
        except ValueError:
            raise ValidationError("Invalid page token.")

        return APIResponse(schema, res)
