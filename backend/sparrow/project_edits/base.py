from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.routing import Route, Router
from starlette.responses import PlainTextResponse, JSONResponse, Response
from webargs_starlette import use_annotations
from webargs import fields
import json

from sqlalchemy import Table, text, select, delete

from .utils import *
from ..context import app_context
 
## TODO: way to delete publications from this route
# maybe have an actions field for query, one would be delete, if that was there it would call a function
# that handles removing that relationship from project. 
# PROBLEM: This solution won't remove the publication completely, as it shouldn't in a real world senario.
# it just removes the foreign id reference. We'll have to just remove them with a quick algorithim or something

class ProjectEdits(HTTPEndpoint):
    async def put(self, request):  
        '''
            Put Endpoint for the project admin page

            NOTE: This route is tested
        '''
        db = app_context().database

        id = request.path_params['id']

        model = db.model.project
        project = db.session.query(model).get(id)

        data = await request.json()
        #data = json.loads(data)
        # need to check for publication field first.
        if "publications" in data:
            response = data.copy()

            #create a publication_collection from the passed publication array of objects
            collection = create_publication_collection(data['publications'], project.publication_collection, db)
            ## create a new field that matches the model collection
            data['publication_collection'] = collection
            data.pop('publications')

            for k in data:
                setattr(project, k, data[k])

            
            db.session.add(project)
            #db.session.commit()
        
            return PlainTextResponse(f'{project.publication_collection}, {response}')
       
        for k in data:
            setattr(project, k, data[k])
        
        db.session.commit()
        
        return JSONResponse(data)

Project_edits_api = Router([
    Route("/edit/{id}", endpoint=ProjectEdits, methods=["PUT"]),
])


