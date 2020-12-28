from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from ..context import app_context
from sqlalchemy import create_engine, MetaData, Table, Column, select
import pandas as pd
import json
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, shape, Point, Polygon


def create_bound_shape(pnts: [float], srid = 4326):
    '''
        Function to create a bounding polygon location filtering 

        points: needs to be 4 numbers long, [minLong, minLat, maxLong, maxLat]
    '''
    #TODO: make it accept any number of points
    points = [pnt for pnt in pnts] ## make sure all values are positive b/c of error
    minLong, minLat, maxLong, maxLat = points

    poly = Polygon([[minLong, minLat],[minLong, maxLat],[maxLong ,minLat], [maxLong, maxLat], [minLong, minLat] ])
    bounding_poly = from_shape(poly, srid=srid)

    return bounding_poly

def get_proj_pub(db):
    '''
    Creates a dataframe that joins publications on projects and contains sample_id to
    merge onto main dataframe in view. 
    '''
    connection = db.engine.connect()

    ## Tables getting mapped using expressional language
    project_pub = Table('project_publication', db.meta, autoload=True, autoload_with=db.engine)
    project_sample = Table('project_sample', db.meta, autoload=True, autoload_with=db.engine)

    ## Select Statments
    project_pub = connection.execute(select([project_pub]))
    project_sample = connection.execute(select([project_sample]))

    ## Turn into pd.DataFrames
    project_pub = pd.DataFrame(project_pub, columns=project_pub.keys())
    project_sample = pd.DataFrame(project_sample, columns=project_sample.keys())

    df = pd.merge(project_sample,project_pub, on='project_id')

    df.drop(['audit_id_x', 'audit_id_y'], axis=1,inplace=True)

    ## Create a Projects dataframe with id and name
    Project = Table('project', db.meta, autoload=True,autoload_with=db.engine)
    Project = connection.execute(select([Project]))
    Projects = pd.DataFrame(Project, columns=Project.keys())
    Projects = Projects[['id','name']]
    Projects.rename(columns={'id':'project_id', 'name':'proj_name'},inplace=True)

    ## Create a Pub dataframe with id and doi
    Pubs = Table('publication', db.meta, autoload=True,autoload_with=db.engine)
    Pubs = connection.execute(select([Pubs]))
    Pubs = pd.DataFrame(Pubs, columns=Pubs.keys())
    Pubs = Pubs[['id','doi']]
    Pubs.rename(columns={'id':'publication_id'}, inplace=True)

    # Merge all together so I have a dataframe with all ids
    df = pd.merge(df,Projects, on='project_id')
    df = pd.merge(df,Pubs,on='publication_id')

    return df

def create_coordinates_from_location(location):
    '''
        Takes location column from database (SIRD:4346;POINT(long,lat)) 
        and turns it into {'type':'point','coordinates':[long,lat]}
    '''
    if location is None:
        return None
    return mapping(to_shape(location))

def create_location_from_coordinates(longitude, latitude):
    '''This function will create the json-like object in database from long & lat given in a post request'''
    location = from_shape(Point(longitude, latitude), srid=4326)
    return location

def make_changes(tablename, changes, session):
    """Function that takes in a list of dictionaries with changes to the database
        
       -tablename: name of table class, sqlalchemy object.
       -changes: list of objects. with changes to be persisted
       -session: current session on the engine.
       
       Creates pending changes, can be seen in the session.dirty
    
    """
    ## TODO: Context manager for the function.. Error checking that would call a session.rollback()
        
    new_changes = project_pub_check(changes)

    for ele in new_changes:

        ## make sure the ID was passed
        if 'id' not in ele:
            raise Exception("You need to pass the row ID")

        ## change the longitude and latitude values to location with the correct format
        if 'longitude' and 'latitude' in ele:
            ele['location'] = create_location_from_coordinates(float(ele['longitude']), float(ele['latitude']))
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

            ## This has to happen otherwise the materials has ()'s and ""'s around it
            current_material_list = []
            for row in current_materials:
                current_material_list.append(row.id)

            if ele['material'] not in current_material_list: 
                db.session.add(Material(id=ele['material']))
                db.session.commit()

def project_pub_check(changes):
    '''
        Handler for incoming changes to projects and publication. For now will just ignore them.
    '''
    proj_pub_list = ['project_id', 'proj_name', 'pub_id','DOI']

    ## Check proj_pub_list contains a field from changes
    # if it does, remove it 
    for ele in changes:
        for i in ele:
            if i in proj_pub_list:
                ele.pop(i)
   
    return changes