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

def create_location_from_coordinates(longitude, latitude):
    '''This function will create the json-like object in database from long & lat given in a post request'''
    location = from_shape(Point(longitude, latitude), srid=4346)
    return location

def make_changes(tablename, changes, session):
    """Function that takes in a list of dictionaries with changes to the database
        
       -tablename: name of table class, sqlalchemy object.
       -changes: list of objects. with changes to be persisted
       -session: current session on the engine.
       
       Creates pending changes, can be seen in the session.dirty
    
    """
    ## TODO: Context manager for the function.. Error checking that would call a session.rollback()
        
    for ele in changes:

        ## make sure the ID was passed
        if 'id' not in ele:
            raise Exception("You need to pass the row ID")

        ## change the longitude and latitude values to location with the correct format
        if 'longitude' and 'latitude' in ele:
            ele['location'] = create_location_from_coordinates(ele['longitude'], ele['latitude'])
            ele.pop('longitude')
            ele.pop('latitude')

        ## get the keys and the id
        query_id = ele['id']
        keys = list(ele.keys())
        keys.remove('id')
        
        ## grab the row we are gonna change
        row = session.query(tablename).filter_by(id=query_id).one()
        
        for item in keys:
            setattr(row, item, ele[item]) ## Set the new value 

def material_check(db, changes):
    '''Checks if material exists in database.
        If passed material is new, it is added to vocabulary.material before the sample is updated.
    '''

    for ele in changes:
        if 'material' not in ele:
            pass
        else:
            Material = db.model.vocabulary_material    
            current_materials = db.session.query(Material).all()

            current_material_list = []
            for row in current_materials:
                current_material_list.append(row.id)

            if ele['material'] not in current_material_list: 
                db.session.add(Material(id=ele['material']))
                db.session.commit()



async def datasheet(request):
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
    ## TODO: Need a way to handle long/lat changes. SRID 4346: POINT(long, lat)

    db = app_context().database ## This gives me access to the Database class

    ## get the data from the post request and turn it into a dict.
    request_data = await request.json()
    request_dict = json.loads(request_data)

    ## grab the sample table from automap_base 
    table = db.model.sample

    ## function to make sure material passed is in vocab_material, if not add it.
    material_check(db, request_dict)

    ## Call my make_changes function
    make_changes(table, request_dict, db.session)

    db.session.commit()
    
    return JSONResponse({"Status": "Success"})

EditApi = Router([
    Route("/datasheet", endpoint=datasheet, methods=["POST"])
])

def construct_edit_app():
    app = Starlette(routes=EditApi)
    return app