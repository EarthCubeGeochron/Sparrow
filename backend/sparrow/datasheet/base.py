from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route, Router


from .utils import *
from .edits import datasheet_edits
from .view import datasheet_view


DatasheetApi = Router(
    [
        Route("/edits", endpoint=datasheet_edits, methods=["POST"]),
        Route("/view", endpoint=datasheet_view, methods=["GET"]),
    ]
)
