from sparrow.core.auth.api import UnauthorizedResponse
from starlette.endpoints import HTTPEndpoint
from webargs_starlette import parser
from webargs.fields import DelimitedList, Str, Int, Boolean
from sqlakeyset import get_page
from marshmallow_sqlalchemy.fields import get_primary_keys
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.authentication import requires
from yaml import safe_load

from ...context import get_database
from ..exceptions import ValidationError, HTTPException, ApplicationError
from ..fields import NestedModelField
from ..response import APIResponse
from ..filters import (
    BaseFilter,
    AuthorityFilter,
    FieldExistsFilter,
    FieldNotExistsFilter,
    _schema_fields,
    EmbargoFilter,
    DateFilter,
    DOIFilter,
    CoordinateFilter,
    GeometryFilter,
    TextSearchFilter,
    AgeRangeFilter,
    IdListFilter,
    TagsFilter,
)
from sparrow.core.open_search.filter import OpenSearchFilter
from ...database.mapper.util import classname_for_table
from ...logs import get_logger
from ...util import relative_path
from ..api_info import (
    model_description,
    model_examples,
    root_example,
    root_info,
    meta_info,
)
from .utils import construct_schema_fields_object

log = get_logger(__name__)


def create_params(description, example):
    """create param description for api docs"""
    return {"description": description, "example": example}


def _field_description(schema, field):
    if schema := getattr(field, "schema", None):
        name = schema.__class__.__name__
        if schema.many:
            name += "[]"
        return name
    return field.__class__.__name__


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

        d = "related models to nest within response [allowed_nests]"
        e = "?nest=session,project"
        des = create_params(d, e)
        self.instance_schema = dict(
            nest=NestedModelField(Str(), missing=[], description=des)
        )

        des_page = create_params("number of results per page", "?page=>i:5039")
        des_per_page = create_params("number of results per page", "?per_page=15")
        des_all = create_params("return all results", "?all=true")

        self.args_schema = dict(
            **self.instance_schema,
            page=Str(missing=None, description=des_page),
            per_page=Int(missing=20, description=des_per_page),
            all=Boolean(missing=False, description=des_all),
        )

        self._filters = []
        self.register_filter(OpenSearchFilter)
        self.register_filter(AuthorityFilter)
        self.register_filter(FieldExistsFilter)
        self.register_filter(FieldNotExistsFilter)
        self.register_filter(EmbargoFilter)
        self.register_filter(DateFilter)
        self.register_filter(DOIFilter)
        self.register_filter(CoordinateFilter)
        self.register_filter(GeometryFilter)
        self.register_filter(TextSearchFilter)
        self.register_filter(AgeRangeFilter)
        self.register_filter(IdListFilter)
        self.register_filter(TagsFilter)

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

    @property
    def description(self):
        return model_description(self.meta.schema)

    @property
    def example(self):
        return model_examples(self.meta.schema)

    def _arg_description(self, field):
        type = field.__class__.__name__.lower()
        if isinstance(field, DelimitedList):
            type = (
                f"list of {field.inner.__class__.__name__.lower()}s (comma-delimited)"
            )
        if d := field.metadata.get("description"):
            type_dict = {"type": type}
            return {**type_dict, **d}
        return type

    def build_param_help(self):
        for k, v in self.args_schema.items():
            yield k, self._arg_description(v)

    async def get_single(self, request):
        """Handler for single instance GET requests"""
        db = get_database()
        id = request.path_params.get("id")
        args = await self.parse_querystring(request, self.instance_schema)

        with db.session_scope(commit=False):
            schema = self.meta.schema(many=False, allowed_nests=args["nest"])
            # This needs to be wrapped in an error-handling block!
            q = db.session.query(schema.opts.model)

            res = q.get(id)
            if not request.user.is_authenticated:
                if res.embargo_date is not None:
                    return UnauthorizedResponse()

            # https://github.com/djrobstep/sqlakeyset
            return APIResponse(res, schema=schema)

    async def api_docs(self, request, schema):
        return JSONResponse(
            {
                "license": "CC-BY 4.0",
                "description": str(self.description),
                "parameters": dict(self.build_param_help()),
                "allowed_nests": list(set(schema._available_nests())),
                "examples": list(self.example),
                "fields": construct_schema_fields_object(schema),
            }
        )

    async def parse_querystring(self, request, schema):
        try:
            args = await parser.parse(schema, request, location="querystring")
            # We don't properly allow 'all' in nested field
            if len(args["nest"]) == 1 and args["nest"][0] == "all":
                args["nest"] = "all"
            log.info(args)
            return args
        except Exception:
            raise ValidationError("Failed parsing query string {request.query_params}")

    async def get(self, request):
        """Handler for all GET requests"""

        if request.path_params.get("id") is not None:
            # Pass off to the single-item handler
            return await self.get_single(request)
        args = await self.parse_querystring(request, self.args_schema)
        db = get_database()

        schema = self.meta.schema(many=True, allowed_nests=args["nest"])
        model = schema.opts.model

        if not len(request.query_params.keys()):
            return await self.api_docs(request, schema)

        # Wrap entire query infrastructure in error-handling block.
        # We should probably make this a "with" statement or something
        # to use throughout our API code.
        with db.session_scope(commit=False):

            q = db.session.query(schema.opts.model)

            for _filter in self._filters:
                q = _filter(q, args)

            if not request.user.is_authenticated and hasattr(
                schema.opts.model, "embargo_date"
            ):
                q = q.filter(schema.opts.model.embargo_date == None)

            q = q.options(*list(schema.query_options(max_depth=None)))

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

    @requires("admin")
    async def put(self, request):
        """Handler for all PUT requests"""

        ## database
        db = self.meta.database

        ## Should be a json object
        data = await request.json()

        ## the data model
        model = self.meta.schema.opts.model
        schema = self.meta.schema()

        ## data needs id since we are only editing in the PUT endpoint
        # two cases, a list of edits are passed, i.e the datasheet. Other just one, admin page
        _type = type(data)
        if _type == list:
            return_data = []
            for ele in data:
                if "id" not in ele:
                    return JSONResponse(
                        {
                            "Error": "No ID was passed, if you are adding a new row please use the POST route"
                        }
                    )
                existing = db.session.query(model).get(ele["id"])
                updates = schema.load(
                    ele, instance=existing, session=db.session, partial=True
                )
                updates.id = existing.id
                db.session.rollback()
                db.session.merge(updates)
                db.session.commit()

                dump = schema.dump(updates)
                return_data.append(dump)
            return JSONResponse(
                {"Status": f"success to {self._model_name}", "data": return_data}
            )
        else:
            id_ = request.path_params.get("id")
            if id_ is None:
                return JSONResponse(
                    {
                        "Error": "No ID was passed, if you are adding a new row please use the POST route"
                    }
                )
            existing = db.session.query(model).get(id_)
            updates = schema.load(
                data, instance=existing, session=db.session, partial=True
            )
            updates.id = existing.id
            db.session.rollback()
            db.session.merge(updates)
            db.session.commit()

            return_data = schema.dump(updates)

            return JSONResponse(
                {"Status": f"success to {self._model_name}", "data": return_data}
            )

    @requires("admin")
    async def post(self, request):
        """
        Handler for all POST requests. i.e, New rows for database

        https://marshmallow-sqlalchemy.readthedocs.io/en/latest/#de-serialize-your-data
        to return data, need to get the schemas by db.interface.model
        the instaniate it, sample_schema = schema()
        then can call sample_schema.dump(sampleModel) deserializes data

        """
        db = self.meta.database

        ## the data model
        model = self.meta.schema.opts.model
        schema = self.meta.schema()

        data = await request.json()

        _type = type(data)
        if _type == list:
            return_data = []
            for ele in data:
                new_row = db.load_data(self._model_name, ele)
                new_row_json = schema.dump(new_row)
                return_data.append(new_row_json)
            return JSONResponse(
                {
                    "status": f"Successfully submitted to {self._model_name}",
                    "data": return_data,
                }
            )

        else:
            new_row = db.load_data(self._model_name, data)
            return_data = schema.dump(new_row)

            return JSONResponse(
                {
                    "status": f"Successfully submitted to {self._model_name}",
                    "data": return_data,
                }
            )

    async def delete(self, request):
        """
        handler of delete requests
        """
        db = self.meta.database

        model = self.meta.schema.opts.model
        schema = self.meta.schema()

        id_ = request.path_params.get("id")
        data_model = db.session.query(model).get(id_)

        return_data = schema.dump(data_model)

        db.session.delete(data_model)
        try:
            db.session.commit()
        except:
            db.session.rollback()

        return JSONResponse({"status": "success", "DELETE": return_data})
