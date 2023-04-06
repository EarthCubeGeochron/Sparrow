from sparrow.core.plugins import SparrowCorePlugin
from sparrow.context import app_context
from sparrow.core.util import relative_path
from sparrow.database.util import run_sql_query_file
from starlette.routing import Route, Router
from starlette.responses import JSONResponse
import pandas as pd
from pathlib import Path
import json


class MapGeoJSONEndpoint(SparrowCorePlugin):
    name = "map-geojson"

    def geojson_view(self):
        db = self.app.database
        p = Path(relative_path(__file__, "geojson.sql"))

        ## returns array of objects, we don't want the key
        geojson = run_sql_query_file(db.session, p)
        a = [v for v, in geojson.fetchall()]  ## very strange tuple unpacking

        return JSONResponse(a)  # a is a list of geojson objects

    def on_api_initialized_v2(self, api):
        root_route = "core_view"
        basic_info = dict(
            route="/core_view/all_samples",
            description="A GeoJSON route for all samples",
        )
        api.add_route(
            "/core_view/all_samples",
            self.geojson_view(),
            methods=["GET"],
            include_in_schema=False,
        )
        api.route_descriptions[root_route].append(basic_info)
