from starlette.routing import Route, Router

from .utils import *
from .edits import datasheet_edits
from .view import datasheet_view

DatasheetAPI = Router([
    Route("/edits", endpoint=datasheet_edits, methods=["POST"]),
    Route("/view", endpoint=datasheet_view, methods=["GET"])
])
