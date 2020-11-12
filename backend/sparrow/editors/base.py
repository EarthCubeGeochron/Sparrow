from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route, Router
from starlette.responses import PlainTextResponse, JSONResponse, Response
from ..context import app_context
from sqlalchemy import create_engine, MetaData, Table, Column
import pandas as pd

async def datasheet(request):
    """
    This will be the end route for the database editing. 
    It will collect changes from the database and find where 
    they belong in the database and then make the change

    Current working, takes in a change and sees if it can pull row out of the db and match it.
    If it works it will return a "Success" 
    """
    db = app_context().database ## This gives me access to the Database class
    data = db.exec_query("SELECT * FROM vocabulary.metrics") ## creates a pandas dataframe from sql
    # if data.columns[0] == 'samples_with_location':
    #     response = {"Status" : "Success"}
    # else:
    #     response = {"Status": "Failure"}
    ##response = JSONResponse(await request.json())
    return PlainTextResponse(data.columns[0])

EditApi = Router([
    Route("/datasheet", endpoint=datasheet, methods=["POST"])
])

def construct_edit_app():
    app = Starlette(routes=EditApi)
    return app