from sparrow.core.plugins import SparrowCorePlugin
from sparrow.core.context import app_context
from macrostrat.database.utils import get_dataframe
from macrostrat.utils import relative_path
from starlette.routing import Route, Router
from starlette.responses import JSONResponse
from pathlib import Path
import json


class MetricsEndpoint(SparrowCorePlugin):
    """
    This Sparrow Plugin adds a GET route to the API.
    It works by reading in a postgreSQL query from a
    file in this directory, querying the sparrow
    database, and then returning the response a JSON.

    It then uses the on_api_initialized_v2 hook to add the route
    and some route documentation that shows up on the api.
    """

    name = "metrics"

    def metrics_view(self):
        db = self.app.database
        p = Path(relative_path(__file__, "metrics.sql"))
        sqlfile = open(p, "r")
        query = sqlfile.read()

        metrics = get_dataframe(db.engine, query)
        res = metrics.to_json(orient="records")

        return JSONResponse(json.loads(res))

    def on_api_initialized_v2(self, api):
        root_route = "core_view"
        basic_info = dict(
            route="/core_view/metrics", description="A metrics route for Sparrow"
        )
        api.add_route(
            "/core_view/metrics",
            self.metrics_view(),
            methods=["GET"],
            include_in_schema=False,
        )
        api.route_descriptions[root_route].append(basic_info)
