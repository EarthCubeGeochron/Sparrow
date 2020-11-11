from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route, Router
from starlette.responses import PlainTextResponse, JSONResponse


def HomePage(request):
    return PlainTextResponse("HomePage for Editing POST requests")

def Datasheet_POST(Request):
    return PlainTextResponse("This is Working on Edits")


EditApi = Router([
    Route("/edits", HomePage),
    Route("/edits/datasheet", endpoint=Datasheet_POST, methods=["POST"])
])

def construct_edit_app():
    app = Starlette(routes=EditApi)
    return app