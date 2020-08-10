"""
A modern application server that translates our primary Sparrow app
(Flask/WSGI) to starlette (ASGI). This is for forward compatibility
with new async server architecture available in Python 3.6+.
"""
from starlette.applications import Starlette
from starlette.routing import Mount, Route, RedirectResponse
from asgiref.wsgi import WsgiToAsgi
from .api import APIv2
from .app import App

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

app = Starlette(routes=routes)
