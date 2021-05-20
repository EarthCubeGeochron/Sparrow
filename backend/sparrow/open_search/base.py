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
        query_params = request.query_params
        if 'query' not in query_params or 'model' not in query_params:
            return JSONResponse(
                {
                    "Status": "Success",
                    "Message": "Provide a string as a query parameter or model",
                    "example": "/api/v2/search?query=lava&model=sample",
                }
            )

        params = {"query": query_params["query"]}
        model = query_params["model"]
        
        if model == "sample":
            sql_fn = search_sample
        elif model == "project":
            sql_fn = search_project
        else:
            sql_fn = search_session

        query_res = db.exec_sql_query(fn = sql_fn, params=params)

        json_res = [dict(r) for r in query_res]

        # res = select_page(db.session, text(sql).selectable, 15)

        return APIResponse(json_res, total_count=len(json_res))


OpenSearchAPI = Router([Route("/query", endpoint=OpenSearchEndpoint, methods=["GET"])])
