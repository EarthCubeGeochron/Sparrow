from starlette.routing import Mount, Route, RedirectResponse
from sparrow.plugins import SparrowCorePlugin
from .core import APIv2

# Shim redirect for root path.
# TODO: clean this up
async def redirect(*args):
    return RedirectResponse("/api/v2/")


class APIv2Plugin(SparrowCorePlugin):
    name = "api-v2"
    sparrow_version = ">=2.*"

    def on_add_routes(self, route_table):
        api_v2 = APIv2(self.app)
        route_table += [
            Route("/api/v2", endpoint=redirect),
            Mount("/api/v2/", app=api_v2),
        ]