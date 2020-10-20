"""
This module houses a
modern application server that translates our primary Sparrow app
(Flask/WSGI) to starlette (ASGI). This is for forward compatibility
with new async server architecture available in Python 3.6+.
"""
import logging
from contextvars import ContextVar
from starlette.applications import Starlette
from starlette.routing import Mount, Route, RedirectResponse
from asgiref.wsgi import WsgiToAsgi
from ..api import APIv2
from ..app import App
from ..logs import console_handler
from ..context import _setup_context

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


def construct_app():
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

    app = Starlette(routes=routes, debug=True)
    flask.run_hook("asgi-setup", app)
    return app
