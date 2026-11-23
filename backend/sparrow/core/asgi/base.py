"""
This module houses a
modern application server that translates our primary Sparrow app
(Flask/WSGI) to starlette (ASGI). This is for forward compatibility
with new async server architecture available in Python 3.6+.
"""

import logging
from contextvars import ContextVar

from asgiref.wsgi import WsgiToAsgi
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Mount, RedirectResponse, Route
from webargs_starlette import parser

from ..api import APIv2
from ..app import App
from ..context import _setup_context
from ..logs import console_handler

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
    app = App(__name__)
    app.load()
    app.load_phase_2()

    api_v2 = APIv2(app)

    _setup_context(app)

    routes = [
        Route("/api/v2", endpoint=redirect),
        Mount("/api/v2/", app=api_v2),
        Mount("/", app=WsgiToAsgi(flask)),
    ]

    _app = Starlette(routes=routes, debug=True)
    app.run_hook("asgi-setup", _app)
    return _app
