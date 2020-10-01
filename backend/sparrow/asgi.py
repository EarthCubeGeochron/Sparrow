"""
A modern application server that translates our primary Sparrow app
(Flask/WSGI) to starlette (ASGI). This is for forward compatibility
with new async server architecture available in Python 3.6+.
"""
import logging
from starlette.applications import Starlette
from starlette.routing import Mount, Route, RedirectResponse
from asgiref.wsgi import WsgiToAsgi
from .api import APIv2
from .app import App
from .logs import console_handler

# Customize Sparrow's root logger so we don't get overridden by uvicorn
# We may want to customize this further eventually
# https://github.com/encode/uvicorn/issues/410
logger = logging.getLogger("sparrow")
if logger.hasHandlers():
    logger.handlers.clear()
logger.addHandler(console_handler)


flask = App(__name__)
flask.load()
flask.load_phase_2()

FlaskApp = WsgiToAsgi(flask)


# Shim redirect for root path.
# TODO: clean this up
async def redirect(*args):
    return RedirectResponse("/api/v2/")


api_v2 = APIv2(flask)

routes = [
    Route("/api/v2", endpoint=redirect),
    Mount("/api/v2/", app=api_v2),
    Mount("/", app=FlaskApp),
]

app = Starlette(routes=routes, debug=True)
