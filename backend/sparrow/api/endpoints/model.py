from starlette.endpoints import HTTPEndpoint
from webargs_starlette import parser
from webargs.fields import DelimitedList, Str, Int, Boolean
from sqlakeyset import get_page
from marshmallow_sqlalchemy.fields import get_primary_keys
from sqlalchemy import desc
from starlette.responses import JSONResponse, PlainTextResponse
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
    EmbargoFilter,
    DateFilter,
    DOI_filter,
    Coordinate_filter,
    Geometry_Filter,
    TextSearchFilter,
    Age_Range_Filter,
    IdListFilter
)
from ...database.mapper.util import classname_for_table
from ...logs import get_logger
from ...util import relative_path
from .utils import location_check, material_check, commit_changes, commit_edits, collection_handler 
import json
import copy

log = get_logger(__name__)

def create_params(description, example):
    '''create param description for api docs'''
    return {"description": description, "example": example}

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

def model_examples(schema):
    name = classname_for_table(schema.opts.model.__table__)
    return api_help["examples"].get(
        name,
         [f"An autogenerated example for the '{name}' model"],
    )
def root_example():
    return api_help["root"]["examples"]
def root_info():
    return api_help["root"]["info"]
def meta_info():
    return api_help['meta']

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
        des = create_params(d,e)
        self.instance_schema = dict(
            nest=NestedModelField(
                Str(),
                missing=[],
                description=des,
            )
        )
        
        des_page = create_params("number of results per page","?page=>i:5039")
        des_per_page = create_params("number of results per page", "?per_page=15")
        des_all = create_params("return all results", "?all=true")

        self.args_schema = dict(
            **self.instance_schema,
            page=Str(missing=None, description=des_page),
            per_page=Int(missing=20, description=des_per_page),
            all=Boolean(missing=False, description=des_all),
        )

        self._filters = []
        self.register_filter(AuthorityFilter)
        self.register_filter(FieldExistsFilter)
        self.register_filter(FieldNotExistsFilter)
        self.register_filter(EmbargoFilter)
        self.register_filter(DateFilter)
        self.register_filter(DOI_filter)
        self.register_filter(Coordinate_filter)
        self.register_filter(Geometry_Filter)
        self.register_filter(TextSearchFilter)
        self.register_filter(Age_Range_Filter)
        self.register_filter(IdListFilter)

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
                "liscense": "CC-BY 4.0",
                "description": str(self.description),
                "parameters": dict(self.build_param_help()),
                "allowed_nests": list(set(schema._available_nests())),
                "examples": list(self.example),
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

        q = self.query(schema) #constructs query to send to database
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

    async def put(self, request):
        """Handler for all PUT requests"""

        ## database
        db = self.meta.database

        ## Should be a json object
        data = await request.json()
        return_data = copy.deepcopy(data)

        ## the data model
        model = self.meta.schema.opts.model

        ## data needs id since we are only editing in the PUT endpoint
        # two cases, a list of edits are passed, i.e the datasheet. Other just one, admin page
        _type = type(data)
        if _type == list:
            data = location_check(data) # reformats location column if need be
            material_check(db,data) # adds material to db if need be
            for ele in data:
                if 'id' not in ele:
                    return JSONResponse({"Error":"No ID was passed, if you are adding a new row please use the POST route"})
                ele = collection_handler(db, ele) ## handles model collections
                commit_edits(db, model, ele)
        else:
            data = location_check(data, array=False)
            material_check(db, data, array=False)
            id_ = request.path_params['id']
            if id_ is None:
                return JSONResponse({"Error":"No ID was passed, if you are adding a new row please use the POST route"})
            data = collection_handler(db,data)
            commit_edits(db,model,data, id_)


        return JSONResponse({"Status": f'success to {self._model_name}', "data": return_data})

    async def post(self, request):
        """
        Handler for all POST requests. i.e, New rows for database

        """
        db = self.meta.database

        ## the data model
        model = self.meta.schema.opts.model

        data = await request.json()
        return_data = copy.deepcopy(data)

        _type = type(data)
        if _type == list:
            ## Checks data for long and lat columns and either creates 
            data = location_check(data)
            ## Checks if material is in data and if it's in database, if not adds it
            material_check(db, data)
            for ele in data:
                ele = collection_handler(db,ele)
                commit_changes(db,model,ele)
        else:
            data = location_check(data, array=False)
            material_check(db, data, array=False)
            data = collection_handler(db,data)
            commit_changes(db, model, data)

        
        return JSONResponse({"Status":f"Successfully submitted to {self._model_name}", 'data': return_data})


