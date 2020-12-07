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
    @use_annotations(location='query')
    async def put(self, request, id: int):  
        '''
            Put Endpoint for the project admin page

            NOTE: This route is tested

            Current functionality: Change things in the project model and publication model based on a Project Model JSON 
            object from project admin page (frontend)
        '''
        db = app_context().database

        model = db.model.project
        project = db.session.query(model).get(id)

        data = json.loads(await request.json())

        new_data = handle_publications(data, db)

        for k in new_data:
            setattr(project, k, new_data[k])
        
        db.session.commit()

        return PlainTextResponse(f'Put Request, {project.name}')

    async def get(self, request):
        return PlainTextResponse("Get Request")
    
    @use_annotations(location='query')
    async def delete(self, request, publication: int = None, sample: int = None):
        '''
            Delete endpoint for the project admin page, can use query args to get id of deleteable stuff
            NOTE: This route is tested

            There seems to be a strange way to access samples from project in APIv2
                project -> session -> sample.

            NOTE: These deletions should only delete the referenced relationships 
            in the database, not the tracked data itself.
        '''

        db = app_context().database
        connection = db.engine.connect()

        edit_project_references(db, publication, "publication")

        ##edit_project_references(db, sample, "sample") Not ready yet

        return PlainTextResponse("Delete Method")

Project_edits_api = Router([
    Route("/edits", endpoint=ProjectEdits, methods=["PUT", "GET", "DELETE"]),
])


