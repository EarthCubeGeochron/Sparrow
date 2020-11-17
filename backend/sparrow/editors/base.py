from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route, Router
from starlette.responses import PlainTextResponse, JSONResponse, Response
from ..context import app_context
from sqlalchemy import create_engine, MetaData, Table, Column
import pandas as pd
import json

def create_geo_from_coordinates(longitude, latitude):
    '''This function will create the json-like object in database from long & lat given in a post request'''
    geo_object = {'type': 'Point', 'coordinates': [longitude, latitude]}
    return geo_object

async def datasheet(request):
    """
    This will be the end route for the database editing. 

    The way to do this is be able to load the Sample table as a Sqlalchemy 
    class object and run update() on it.

    Current working on, takes in a change and sees if it can pull row out of the db and match it.
    If it works it will return a "Success" 

    Use the automap_base() to create classes we can do sessions on
    https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html

    And then edit a class object directly by changing a specific value like here
    https://docs.sqlalchemy.org/en/13/orm/tutorial.html#adding-and-updating-objects

    Create a function that reflects database. Then queries to find row that has been changed. 
    Then modify the value on that row, which is an automap object. Then commits it.

    """
    db = app_context().database ## This gives me access to the Database class

    request_data = await request.json()
    request_dict = json.loads(request_data)

    df = pd.DataFrame.from_dict([request_dict]); ## dataframe of incoming changes
    
    query_id = request_dict['id']
    query_string = f"SELECT * FROM core_view.sample s WHERE s.id = {query_id}"
    
    ## For some reason data is empty. All the dataframes in the tests are empty
    data = db.exec_query(query_string) ## creates a pandas dataframe from sql

    columns = data.columns.tolist()
    ## Loops through dataframes and checks for differences. Maybe use a where statement to align at id
    for i in columns:
        for index, s in df.iterrows():
            if data[i][index] != df[i][index]:
                return df[i][index] 


    response = data['name']
    eror
    return PlainTextResponse('response[0]')

EditApi = Router([
    Route("/datasheet", endpoint=datasheet, methods=["POST"])
])

def construct_edit_app():
    app = Starlette(routes=EditApi)
    return app