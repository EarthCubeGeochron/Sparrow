from flama.exceptions import ValidationError
from starlette.endpoints import HTTPEndpoint
from webargs_starlette import parser
from webargs.fields import DelimitedList, Str, Int
from sqlakeyset import get_page
from marshmallow_sqlalchemy.fields import get_primary_keys
from sqlalchemy import desc
from starlette.responses import JSONResponse

from ..database.mapper.util import classname_for_table
from ..logs import get_logger
from .response import APIResponse
from ..util import relative_path
from yaml import safe_load

log = get_logger(__name__)


def _schema_fields(schema):
    return None
    return {getattr(f, "data_key", k): f for k, f in schema.fields.items()}


with open(relative_path(__file__, "api-help.yaml"), "r") as f:
    api_help = safe_load(f)


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
        self._model_name = classname_for_table(schema.opts.model.__table__)
        log.info(self._model_name)

        self.instance_schema = dict(nest=DelimitedList(Str(), missing=[]),)

        self.args_schema = dict(
            **self.instance_schema,
            has=DelimitedList(Str(), missing=[]),
            not_has=DelimitedList(Str(), missing=[]),
            page=Str(missing=None),
            per_page=Int(missing=20),
        )

    def query(self, schema):
        db = self.meta.database
        return db.session.query(schema.opts.model)

    @property
    def description(self):
        return api_help["models"].get(
            self._model_name,
            f"An autogenerated route for the '{self._model_name}' model",
        )

    async def get_single(self, request):
        """Handler for single instance GET requests"""
        args = await parser.parse(self.instance_schema, request, location="querystring")
        id = request.path_params.get("id")
        log.info(id, args)

        schema = self.meta.schema(many=False, allowed_nests=args["nest"])
        res = self.query(schema).get(id)
        # https://github.com/djrobstep/sqlakeyset
        return APIResponse(schema, res)

    async def api_docs(self, request, schema):
        return JSONResponse(
            {
                "description": str(self.description),
                "parameters": {
                    "has": "string, model field",
                    "not_has": "string, model field",
                    "per_page": "integer, number of results per page",
                    "page": "string, token of the page to fetch",
                },
                "allowed_nests": [],
                "fields": _schema_fields(schema),
            }
        )

    async def get(self, request):
        """Handler for all GET requests"""

        if request.path_params.get("id") is not None:
            # Pass off to the single-item handler
            return await self.get_single(request)

        log.info(request)
        log.info(request.query_params)
        args = await parser.parse(self.args_schema, request, location="querystring")
        log.info(args)

        schema = self.meta.schema(many=True, allowed_nests=args["nest"])
        model = schema.opts.model

        if not len(request.query_params.keys()):
            return await self.api_docs(request, schema)

        q = self.query(schema)

        fields = _schema_fields(schema)

        filters = []

        # for field in fields:
        #     ## We'll put field-specific filters here
        #     pass

        # Filter by has
        for has_field in args["has"]:
            try:
                field = fields[has_field]
            except KeyError:
                raise ValidationError(f"'{has_field}' is not a valid field")
            orm_attr = getattr(model, field.name)

            if hasattr(field, "related_model"):
                if orm_attr.property.uselist:
                    filters.append(orm_attr.any())
                else:
                    filters.append(orm_attr.has())
            else:
                filters.append(orm_attr.isnot(None))

        # Filter by not_has
        for k in args["not_has"]:
            try:
                field = fields[k]
            except KeyError:
                raise ValidationError(f"'{k}' is not a valid field")
            orm_attr = getattr(model, field.name)

            if hasattr(field, "related_model"):
                if orm_attr.property.uselist:
                    filters.append(~orm_attr.any())
                else:
                    filters.append(~orm_attr.has())
            else:
                filters.append(orm_attr.is_(None))

        for filter in filters:
            q = q.filter(filter)

        # By default, we order by the "natural" order of Primary Keys. This
        # is not really what we want in most cases, probably.
        pk = [desc(p) for p in get_primary_keys(model)]
        q = q.order_by(*pk)
        # https://github.com/djrobstep/sqlakeyset
        try:
            res = get_page(q, per_page=args["per_page"], page=args["page"])
        except ValueError:
            raise ValidationError("Invalid page token.")

        return APIResponse(schema, res, total_count=q.count())
