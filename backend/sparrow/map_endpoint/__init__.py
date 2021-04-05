from sparrow.plugins import SparrowCorePlugin
from sparrow.context import app_context
from sparrow.util import relative_path
from starlette.routing import Route, Router
from starlette.responses import JSONResponse
import pandas as pd
from pathlib import Path
import json

class MapGeoJSONEndpoint(SparrowCorePlugin):

    name = 'map-geojson'

    def geojson_view(self):

        db = self.app.database
        p = Path(relative_path(__file__, "geojson.sql"))
        sqlfile = open(p, "r")
        query = sqlfile.read()

        geojson = db.session.execute(query)
        a = []
        for r in geojson:
            for c,v in r.items():
                a.append(v)

        return JSONResponse(a)

    def on_api_initialized_v2(self, api):

        root_route = "core_view"
        basic_info = dict(
            route="/core_view/geojson",
            description="A GeoJSON route for samples",
        )
        api.add_route("/core_view/geojson", self.geojson_view(), methods=["GET"], include_in_schema=False)
        api.route_descriptions[root_route].append(basic_info)