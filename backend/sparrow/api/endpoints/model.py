from starlette.endpoints import HTTPEndpoint
from webargs_starlette import parser
from webargs.fields import DelimitedList, Str, Int, Boolean
from sqlakeyset import get_page
from marshmallow_sqlalchemy.fields import get_primary_keys
from sqlalchemy import desc
from starlette.responses import JSONResponse
from yaml import safe_load

from ..exceptions import ValidationError
from ..fields import NestedModelField
from ..response import APIResponse
from ..filters import (
    BaseFilter,
    AuthorityFilter,
    FieldExistsFilter,
    FieldNotExistsFilter,
    _schema_fields,
)
from ...database.mapper.util import classname_for_table
from ...logs import get_logger
from ...util import relative_path

log = get_logger(__name__)


def _field_description(schema, field):
    if schema := getattr(field, "schema", None):
        name = schema.__class__.__name__
        if schema.many:
            name += "[]"
        return name
    return field.__class__.__name__


with open(relative_path(__file__, "..", "api-help.yaml"), "r") as f:
    api_help = safe_load(f)


def model_description(schema):
    name = classname_for_table(schema.opts.model.__table__)
    return api_help["models"].get(
        name,
        f"An autogenerated route for the '{name}' model",
    )


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

        self.instance_schema = dict(
            nest=NestedModelField(
                Str(),
                missing=[],
                description="related models to nest within response [allowed_nests]",
            )
        )

        self.args_schema = dict(
            **self.instance_schema,
            page=Str(missing=None, description="number of results per page"),
            per_page=Int(missing=20, description="token of the page to fetch"),
            all=Boolean(missing=False, description="return all results"),
        )

        self._filters = []
        self.register_filter(AuthorityFilter)
        self.register_filter(FieldExistsFilter)
        self.register_filter(FieldNotExistsFilter)

    @property
    def model(self):
        return self.meta.schema.opts.model

    def register_filter(self, _filter: BaseFilter):
        """Register a filter specification to control parametrization of the
        model query"""
        f = _filter(self.model, schema=self.meta.schema)
        if not f.should_apply():
            return
        if params := getattr(f, "params"):
            self.args_schema.update(**params)
        self._filters.append(f)

    def query(self, schema):
        db = self.meta.database
        return db.session.query(schema.opts.model)

    @property
    def description(self):
        return model_description(self.meta.schema)

    def _arg_description(self, field):
        type = field.__class__.__name__.lower()
        if isinstance(field, DelimitedList):
            type = (
                f"list of {field.inner.__class__.__name__.lower()}s (comma-delimited)"
            )
        if d := field.metadata.get("description"):
            type += ", " + d
        return type

    def build_param_help(self):
        for k, v in self.args_schema.items():
            yield k, self._arg_description(v)

    async def get_single(self, request):
        """Handler for single instance GET requests"""
        args = await parser.parse(self.instance_schema, request, location="querystring")
        id = request.path_params.get("id")
        log.info(request.query_params)

        schema = self.meta.schema(many=False, allowed_nests=args["nest"])
        res = self.query(schema).get(id)
        # https://github.com/djrobstep/sqlakeyset
        return APIResponse(res, schema=schema)

    async def api_docs(self, request, schema):
        return JSONResponse(
            {
                "description": str(self.description),
                "parameters": dict(self.build_param_help()),
                "allowed_nests": list(set(schema._available_nests())),
                "fields": {
                    k: _field_description(schema, v)
                    for k, v in _schema_fields(schema).items()
                },
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

        # We don't properly allow 'all' in nested field
        if len(args["nest"]) == 1 and args["nest"][0] == "all":
            args["nest"] = "all"
        log.info(args["nest"])

        schema = self.meta.schema(many=True, allowed_nests=args["nest"])
        model = schema.opts.model

        if not len(request.query_params.keys()):
            return await self.api_docs(request, schema)

        q = self.query(schema)
        for _filter in self._filters:
            q = _filter(q, args)

        if args["all"]:
            res = q.all()
            return APIResponse(res, schema=schema, total_count=len(res))

        # By default, we order by the "natural" order of Primary Keys. This
        # is not really what we want in most cases, probably.
        pk = [desc(p) for p in get_primary_keys(model)]
        q = q.order_by(*pk)
        # https://github.com/djrobstep/sqlakeyset
        try:
            res = get_page(q, per_page=args["per_page"], page=args["page"])
        except ValueError:
            raise ValidationError("Invalid page token.")

        return APIResponse(res, schema=schema, total_count=q.count())