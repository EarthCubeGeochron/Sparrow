"""
This module houses a
modern application server that translates our primary Sparrow app
(Flask/WSGI) to starlette (ASGI). This is for forward compatibility
with new async server architecture available in Python 3.6+.
"""
from starlette.applications import Starlette
from starlette.routing import Mount, Route, RedirectResponse
from asgiref.wsgi import WsgiToAsgi
from ..api import APIv2
from .flask import App
from ..context import _setup_context
from webargs_starlette import WebargsHTTPException
from starlette.responses import JSONResponse

# For some reason, adding logging in this file seems to kill logging in the entire
# application


# Customize Sparrow's root logger so we don't get overridden by uvicorn
# We may want to customize this further eventually
# https://github.com/encode/uvicorn/issues/410
# logger = logging.getLogger("sparrow")
# if logger.hasHandlers():
#     logger.handlers.clear()
# logger.addHandler(console_handler)

# Shim redirect for root path.
# TODO: clean this up


async def redirect(*args):
    return RedirectResponse("/api/v2/")


async def http_exception(request, exc):
    return JSONResponse(exc.messages, status_code=exc.status_code, headers=exc.headers)


class Sparrow(Starlette):
    def __init__(self, *args, **kwargs):
        flask = App(__name__)
        flask.load()
        flask.load_phase_2()

        api_v2 = APIv2(flask)

        _setup_context(flask)

        routes = [
            Route("/api/v2", endpoint=redirect),
            Mount("/api/v2/", app=api_v2),
            Mount("/", app=WsgiToAsgi(flask)),
        ]

        super().__init__(routes=routes, *args, **kwargs)
        flask.run_hook("asgi-setup", self)
        self.flask = flask

        # This could maybe be added to the API...
        self.add_exception_handler(WebargsHTTPException, http_exception)
