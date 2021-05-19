from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route, Router
from starlette.responses import JSONResponse
from sqlakeyset import select_page
from pathlib import Path
import json

from ..context import app_context
from sparrow.api.response import APIResponse

here = Path(__file__).parent
queries = here / "queries"
search_project = queries / "open-search-project.sql"
search_sample = queries / "open-search-sample.sql"
search_session = queries / "open-search-session.sql"


class OpenSearchEndpoint(HTTPEndpoint):
    async def get(self, request):

        db = app_context().database
        params = request.query_params
        if len(params) == 0:
            return JSONResponse(
                {
                    "Status": "Success",
                    "Message": "Provide a string as a query parameter",
                    "example": "/api/v2/search?query=lava",
                }
            )

        model = params["model"]
        if model == "sample":
            sql = open(search_sample).read()
        if model == "project":
            sql = open(search_project).read()
        if model == "session":
            sql = open(search_session).read()

        query_res = db.session.execute(sql, {"query": params["query"]})

        json_res = [dict(r) for r in query_res]

        # res = select_page(db.session, text(sql).selectable, 15)

        return APIResponse(json_res, total_count=len(json_res))


Open_Search_API = Router([Route("/query", endpoint=OpenSearchEndpoint, methods=["GET"])])
