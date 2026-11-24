import time

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from sparrow.logs import get_logger

from .exceptions import SparrowAPIError

log = get_logger(__name__)


async def http_exception(request, exc):
    log.error(f"{exc.status_code} {exc.detail}")
    log.exception(exc)
    return JSONResponse(
        {"error": {"detail": exc.detail, "status_code": exc.status_code}},
        status_code=exc.status_code,
    )


exception_handlers = {HTTPException: http_exception, SparrowAPIError: http_exception}


async def api_entry(request):
    """What this service does. Reading and editing data is PostgREST's job."""
    return JSONResponse(
        {
            "description": "Sparrow's application services",
            "routes": dict(request.app.route_descriptions),
            "data": "Data is served by PostgREST, at /api/v3 on a lab's gateway.",
        }
    )


class ServerTimings(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        dur = (time.time() - start) * 1e3
        response.headers["Server-Timing"] = f"total;dur={dur}"
        return response


class APIv2(Starlette):
    """
    The services that need application code: signing in, loading records,
    fetching data files and running tasks. Plugins mount them here.
    """

    def __init__(self, app):
        self._app = app
        self.route_descriptions = {}

        super().__init__(exception_handlers=exception_handlers, debug=True)
        self.add_middleware(ServerTimings)
        self.add_route("/", api_entry)
        self._app.run_hook("api-initialized-v2", self)

    def add_route(self, path, *args, **kwargs):
        desc = kwargs.pop("help", None)
        if desc is not None:
            self.route_descriptions[path] = desc

        super().add_route(path, *args, **kwargs)

    def mount(self, path, app, **kwargs):
        desc = kwargs.pop("help", None)
        if desc is not None:
            self.route_descriptions[path] = desc
        super().mount(path, app, **kwargs)
