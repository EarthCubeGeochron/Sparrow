from sqlakeyset import select_page
from sqlalchemy.sql import select, text
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from webargs.fields import Boolean, Int, Str
from webargs_starlette import parser

from sparrow.api.exceptions import ValidationError
from sparrow.api.response import APIResponse
from sparrow.core.context import get_database


class BaseSelectableAPI(HTTPEndpoint):
    """A base class for all selectable endpoints"""

    def __init__(self) -> None:
        super().__init__()
        self.arg_schema = dict(
            page=Str(missing=None, description="Page"),
            per_page=Int(missing=20, description="Number to show"),
            all=Boolean(missing=False, description="Return all results."),
        )
        self.fields = {}
        self.basic_info = {}
        self.schema = None

    def on_api_v2_initialized(self, api):
        root_route = "selectables"
        if self.basic_info is not None:
            api.route_descriptions[root_route].append(self.basic_info)

    async def api_docs(self):
        return JSONResponse(
            {
                "license": "CC-BY 4.0",
                "description": str(self.description),
                "fields": {k: v for k, v in self.fields.items()},
            }
        )
