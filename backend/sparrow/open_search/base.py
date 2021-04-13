from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route, Router
from sqlalchemy import text, select
from starlette.responses import JSONResponse, PlainTextResponse
from sqlakeyset import select_page
from pathlib import Path
import json

from ..context import app_context
from sparrow.api.response import APIResponse

here = Path(__file__).parent
open_search_file = here / "open-search.sql"

class OpenSearchEndpoint(HTTPEndpoint):

    async def get(self, request):

        db = app_context().database
        params = request.query_params
        if len(params) == 0:
            return JSONResponse({"Status":"Success", "Message": "Provide a string as a query parameter", "example": "/api/v2/search?query=lava"})

        sql = open(open_search_file).read()

        query_res = db.session.execute(sql, params)

        json_res = [dict(r) for r in query_res]
        
        #res = select_page(db.session, text(sql).selectable, 15)

        return APIResponse(json_res, total_count=len(json_res))


Open_Search_API = Router(
    [
        Route("/search", endpoint=OpenSearchEndpoint, methods = ["GET"])
    ]
)





