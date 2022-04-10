from starlette.endpoints import HTTPEndpoint
from webargs_starlette import parser
from webargs.fields import Str, Int, Boolean
from sqlakeyset import get_page
from starlette.responses import JSONResponse

from ..exceptions import ValidationError
from ..response import APIResponse
from ...database.mapper.util import classname_for_table
from ...logs import get_logger
from ...context import get_database

log = get_logger(__name__)


class ViewAPIEndpoint(HTTPEndpoint):
    class Meta:
        table = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = self.Meta()
        if getattr(self.meta, "table") is None:
            raise ValueError(f"Meta value '{k}' must be provided for ViewAPIEndpoint")

        self._model_name = classname_for_table(self.meta.table)
        log.info(self._model_name)

        self.args_schema = dict(
            page=Str(missing=None), per_page=Int(missing=20), all=Boolean(missing=False)
        )

    async def get(self, request):
        """Handler for all GET requests"""
        db = get_database()

        log.info(request.query_params)
        args = await parser.parse(self.args_schema, request, location="querystring")
        log.info(args)

        ## This is why the response was blank
        # if not len(request.query_params.keys()):
        #     return JSONResponse({"Hello": "World"})

        q = db.session.query(self.meta.table)
        if args["all"]:
            res = q.all()
            return APIResponse(res, total_count=len(res), to_dict=True)

        try:
            res = get_page(q, per_page=args["per_page"], page=args["page"])
        except ValueError:
            raise ValidationError("Invalid page token.")

        return APIResponse(res, total_count=q.count(), to_dict=True)
