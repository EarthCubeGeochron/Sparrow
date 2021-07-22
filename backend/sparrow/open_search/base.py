from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route, Router
from starlette.responses import JSONResponse, PlainTextResponse
from sqlakeyset import select_page
from webargs.fields import Str, Int, Boolean, DelimitedList
from pathlib import Path
import json

from ..context import app_context
from sparrow.api.response import APIResponse

here = Path(__file__).parent
queries = here / "queries"
search_project = queries / "open-search-project.sql"
search_sample = queries / "open-search-sample.sql"
search_session = queries / "open-search-session.sql"
search_total = queries / "open-search.sql"


class OpenSearchEndpoint(HTTPEndpoint):

    args_schema = dict(
        page=Str(missing=None, description="Page"),
        per_page=Int(missing=20, description="Number to show"),
        all=Boolean(missing=False, description="Return all results."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self, request):

        db = app_context().database
        query_params = request.query_params
        if "query" not in query_params or "model" not in query_params:
            return JSONResponse(
                {
                    "Status": "Success",
                    "Message": "Provide a string as a query parameter or model",
                    "example": "/api/v2/search?query=lava&model=sample",
                }
            )

        params = {"query": query_params["query"]}
        model = query_params["model"]

        models = {
            "sample": search_sample,
            "project": search_project,
            "session": search_session,
        }
        if model == "all":
            sql_fn = search_total
            query_res = db.exec_sql_query(fn=sql_fn, params=params)

            json_res = [dict(model=x, data=y) for x, y in query_res]
            json_res.reverse()

            return JSONResponse(json_res)
        else:
            for key, value in models.items():
                if model == key:
                    sql_fn = value
                    schema = getattr(db.interface, key)(many=True)

        query_res = db.exec_sql_query(fn=sql_fn, params=params)

        json_res = [dict(r) for r in query_res]

        return APIResponse(json_res, total_count=len(json_res), schema=schema)


OpenSearchAPI = Router([Route("/query", endpoint=OpenSearchEndpoint, methods=["GET"])])
