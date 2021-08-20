from sparrow.api.response import APIResponse
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from webargs_starlette import parser
from webargs.fields import DelimitedList, Str, Int, Boolean
from sqlakeyset import get_page,select_page

from ...context import get_database
from ..exceptions import ValidationError, HTTPException, ApplicationError

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
from sparrow.open_search.filter import OpenSearchFilter

class BaseEndpoint(HTTPEndpoint):
    """
        A base endpoint to wrap shared functionality among various endpoints
    """

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args_schema = dict(
            page=Str(missing=None, description="Page"),
            per_page=Int(missing=20, description="Number to show"),
            all=Boolean(missing=False, description="Return all results."),
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
    
    def register_filter(self, _filter: BaseFilter):
        """Register a filter specification to control parametrization of the
        model query"""
        f = _filter(self.model, schema=self.schema)
        if not f.should_apply():
            return
        if params := getattr(f, "params"):
            self.args_schema.update(**params)
        self._filters.append(f)

    def form_query(self, db):
        pass

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
                q = self.form_query(db)

                if not request.user.is_authenticated and hasattr(
                    self.model, "embargo_date"
                    ):
                    q = q.filter(self.model.embargo_date == None)

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
