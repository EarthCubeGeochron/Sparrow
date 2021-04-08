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

        ## returns array of objects, we don't want the key
        geojson = db.session.execute(query)
        a = []
        for r in geojson:
            # r is an object with the geojson as the value
            # we iterate through all key, value pairs 
            # and only append the value (geojson) to return
            for key,value in r.items():
                a.append(value)

        return JSONResponse(a) # a is a list of geojson objects

    def on_api_initialized_v2(self, api):

        root_route = "core_view"
        basic_info = dict(
            route="/core_view/all_samples",
            description="A GeoJSON route for all samples",
        )
        api.add_route("/core_view/all_samples", self.geojson_view(), methods=["GET"], include_in_schema=False)
        api.route_descriptions[root_route].append(basic_info)