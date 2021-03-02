from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route, Router
from starlette.responses import PlainTextResponse, JSONResponse, Response
from ..context import app_context
from sqlalchemy import create_engine, MetaData, Table, Column
import pandas as pd
import json
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape, Point

from .utils import material_check, make_changes

async def datasheet_edits(request):
    """
    This will be the end route for the database editing. 

    The way to do this is be able to load the Sample table as a Sqlalchemy 
    class object and run update() on it.

    Use the automap_base() to create classes we can do sessions on
    https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html

    And then edit a class object directly by changing a specific value like here
    https://docs.sqlalchemy.org/en/13/orm/tutorial.html#adding-and-updating-objects

    db.model: list of automap_base models
    setattr(): a python function that will allow us to edit the automapped object
        setattr(model_name, edit_field, new_value) where edit_field is a string and model_name is the query object

    Recieved request data should be only the changes and the id.

    """
    ## TODO: Handle an incoming Project and Publcation Change, That is a DIFFERENT TABLE.
    ## The issue is, we need to add some foriegn keys to the project and sample...
    ## add the project to the project_sample table and then publication to the project_pub table
    ## For NOW: fix by associating pub with the project that the sample is associated with..
    ## If there are more than one publications leave it uneditable and have a button that goes 
    # to sample the project page
    ## Try to create a relationship between the session and project and publication maybe

    db = app_context().database ## This gives me access to the Database class

    ## get the data from the post request and turn it into a dict.
    request_data = await request.json()

    ## for some reason this wasn't working with real request, only for tests...
    #request_dict = json.loads(request_data)

    ## grab the sample table from automap_base 
    table = db.model.sample

    ## function to make sure material passed is in vocab_material, if not add it.
    material_check(db, request_data)

    ## Call my make_changes function
    make_changes(table, request_data, db.session)

    db.session.commit()
    return JSONResponse({"Status": "Success"})