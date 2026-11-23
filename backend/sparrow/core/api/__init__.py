from starlette.routing import Mount, RedirectResponse, Route

from sparrow.core.plugins import SparrowCorePlugin

# isort: off
# The exceptions module imports the response from this package
from .core import APIv2
from .response import APIResponse
from .exceptions import SparrowAPIError

# isort: on


# Shim redirect for root path.
# TODO: clean this up
async def redirect(*args):
    return RedirectResponse("/api/v2/")


class APIv2Plugin(SparrowCorePlugin):
    name = "api-v2"
    sparrow_version = "==3.*"

    def on_add_routes(self, route_table):
        api_v2 = APIv2(self.app)
        route_table += [
            Route("/api/v2", endpoint=redirect),
            Mount("/api/v2/", app=api_v2),
        ]
