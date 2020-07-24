"""
A modern application server that translates our primary Sparrow app
(Flask/WSGI) to starlette (ASGI). This is for forward compatibility
with new async server architecture available in Python 3.6+.
"""
from starlette.applications import Starlette
from starlette.routing import Mount
from asgiref.wsgi import WsgiToAsgi
from .api import APIv2
from .app import App

flask = App(__name__)
flask.load()
flask.load_phase_2()

FlaskApp = WsgiToAsgi(flask)

routes = [Mount("/api/v2", app=APIv2), Mount("/", app=FlaskApp)]

app = Starlette(routes=routes)
