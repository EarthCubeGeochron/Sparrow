from logging import error
from starlette.endpoints import HTTPEndpoint
from sparrow_utils.logs import get_logger
from webargs_starlette import parser
from sqlakeyset import get_page
from starlette.responses import JSONResponse
from webargs.fields import Str, Int, Boolean, DelimitedList
from sparrow.context import get_database
from sparrow.open_search.filter import OpenSearchFilter
from ...exceptions import SparrowAPIError, ValidationError, ApplicationError
from ...response import APIResponse
from ...filters import (
    BaseFilter,
    AuthorityFilter,
    FieldExistsFilter,
    FieldNotExistsFilter,
    EmbargoFilter,
    DateFilter,
    TextSearchFilter,
    AgeRangeFilter,
    IdListFilter,
    TagsFilter,
)


log = get_logger(__name__)


class DataFileListEndpoint(HTTPEndpoint):
    """A simple demonstration endpoint for paginating a select statement. Extremely quick, but somewhat hand-constructed."""

    args_schema = dict(
        page=Str(missing=None, description="Page"),
        per_page=Int(missing=20, description="Number to show"),
        all=Boolean(missing=False, description="Return all results."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db = get_database()
        self.schema = db.interface.data_file
        self.model = db.model.data_file

        self._filters = []
        self.register_filter(OpenSearchFilter)
        self.register_filter(AuthorityFilter)
        self.register_filter(FieldExistsFilter)
        self.register_filter(FieldNotExistsFilter)
        self.register_filter(EmbargoFilter)
        self.register_filter(DateFilter)
        self.register_filter(TextSearchFilter)
        self.register_filter(AgeRangeFilter)
        self.register_filter(IdListFilter)
        self.register_filter(TagsFilter)

    def register_filter(self, _filter: BaseFilter):
        """Register a filter specification to control parametrization of the
        model query"""
        f = _filter(self.model, schema=self.schema)
        if not f.should_apply():
            return
        if params := getattr(f, "params"):
            self.args_schema.update(**params)
        self._filters.append(f)

    async def get(self, request):
        """Handler for all GET requests"""

        args = await parser.parse(self.args_schema, request, location="querystring")

        db = get_database()

        if not len(request.query_params.keys()):
            return JSONResponse({})

        # Wrap entire query infrastructure in error-handling block.
        # We should probably make this a "with" statement or something
        # to use throughout our API code.
        with db.session_scope(commit=False):

            try:
                DataFile = self.model

                q = db.session.query(
                    DataFile.file_hash,
                    DataFile.file_mtime,
                    DataFile.basename,
                    DataFile.type_id,
                ).order_by(DataFile.file_mtime)

                if args["all"]:
                    res = q.all()
                    return APIResponse(
                        res, schema=self.schema(many=True), total_count=len(res)
                    )

                for _filter in self._filters:
                    q = _filter(q, args)

                try:
                    res = get_page(q, per_page=args["per_page"], page=args["page"])

                except ValueError:
                    raise ValidationError("Invalid page token.")

                # Note: we don't need to use a schema to serialize here. but it is nice if we have it
                return APIResponse(res, schema=self.schema(many=True))
            except Exception as err:
                raise ApplicationError(str(err))


class DataFileFilterByModelID(HTTPEndpoint):
    """
    A filterable datafile endpoint to find related models

    creates a custom json serialization that returns the model with id of the link
    """

    args_schema = dict(
        sample_id=DelimitedList(Int(), description="sample id to filter datafile by"),
        session_id=DelimitedList(Int(), description="session id to filter datafile by"),
        analysis_id=DelimitedList(
            Int(), description="analysis id to filter datafile by"
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.schema = get_database().interface.data_file(
        #     many=True, allow_nests=["data_file_link"]
        # )

    async def get(self, request):
        """Handler for all GET requests"""

        model_names = await parser.parse(
            self.args_schema, request, location="querystring"
        )

        db = get_database()

        n_models = sum(len(v) for v in model_names.values())
        if n_models == 0:
            raise SparrowAPIError("No IDs were passed to filter by")

        # Wrap entire query infrastructure in error-handling block.
        # We should probably make this a "with" statement or something
        # to use throughout our API code.
        with db.session_scope(commit=False):

            DataFile = db.model.data_file
            DataFileLink = db.model.data_file_link

            data = []
            for model_name, model_ids in model_names.items():

                q = db.session.query(
                    DataFile.file_hash,
                    DataFile.file_mtime,
                    DataFile.basename,
                    DataFile.type_id,
                    getattr(DataFileLink, model_name),
                ).order_by(DataFile.file_mtime)

                q = q.join(DataFile.data_file_link_collection).filter(
                    getattr(DataFileLink, model_name).in_(model_ids)
                )

                res = q.all()

                # SUPER messy way to create a custom json serialization
                for row in res:
                    row_obj = {}
                    file_hash, file_mtime, basename, type_id, model_id = row
                    row_obj["file_hash"] = file_hash
                    row_obj["file_mtime"] = file_mtime.isoformat()
                    row_obj["basename"] = basename
                    row_obj["type"] = type_id
                    row_obj["model"] = model_name[:-3]
                    row_obj["model_id"] = model_id
                    data.append(row_obj)

            return JSONResponse(dict(data=data, total_count=len(data)))
