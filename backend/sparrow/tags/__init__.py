from sparrow.plugins import SparrowCorePlugin
from sparrow.context import app_context
from starlette.responses import JSONResponse
from starlette.routing import Route, Router
from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from psycopg2 import sql
from pathlib import Path
import json


here = Path(__file__).parent
fixtures = here / "fixtures"
queries = here / "queries"
procedures = here/"procedures"

class TagsEdits(HTTPEndpoint):
    """
    Tags endpoint for adding and removing tag relationships from models.
    SQL assisted, for a current replacement for schemas.
    """
    name = "TagsEdits"
    add_project_fn = procedures / "add-tag-project.sql"
    add_sample_fn = procedures / "add-tag-sample.sql"
    add_session_fn = procedures / "add-tag-session.sql"
    add_analysis_fn = procedures / "add-tag-analysis.sql"
    add_datum_fn = procedures / "add-tag-datum.sql"
    remove_fn = procedures / "remove-tag-from-model.sql"

    def execute_sql(self, model, data,fn):
        '''
        Put and delete share everything except the sql file.
        '''
        db = app_context().database

        tag_ids = data['tag_ids']
        
        for tag_id in tag_ids:
            params = {"model_id": data['model_id'], "tag_id":tag_id}
            
            db.exec_sql(fn = fn, params=params)

    @requires("admin")
    async def put(self, request):
        """
        Adds a tag model relationship by adding ids to the join table

        """
        model = request.path_params['model']
        data = await request.json()

        fn = ""
        if model == "project":
            fn = self.add_project_fn
        if model == "sample":
            fn = self.add_sample_fn
        if model == "session":
            fn = self.add_session_fn;
        if model == "analysis":
            fn = self.add_analysis_fn
        if model == "datum":
            fn = self.add_datum_fn 
        
        #try:
        self.execute_sql(model, data, fn)
        return JSONResponse({"Status":"Success"})
        #except:
         #   return JSONResponse({"Error":"Something went wrong??"})

    @requires("admin")
    async def delete(self, request):
        '''
        Remove a tag from a model relationship by removing ids from join table
        
        '''
        model = request.path_params['model']
        data = await request.json()

        try:
            self.execute_sql(model, data, self.remove_fn)
            return JSONResponse({"Status":"Success"})
        except:
            return JSONResponse({"Error":"Something went wrong??"})

TagsEditsRouter = Router([Route("/models/{model}", endpoint=TagsEdits, methods=["PUT", "DELETE"])])


class Tags(SparrowCorePlugin):
    """
    Tags implementation, create a new database schema and tables.
    And create API routes, get,post, and delete

    These routes are specific to the tag model only.. the relationship
    will show up in those respective models
    """

    name = "tags"

    ## database-available hook is before the automapper
    def on_core_tables_initialized(self, db):
        """
        Creates schema and tables for tags
        """
        f = fixtures / "tags.sql"
        db.exec_sql(f)

    def get_tags(self):
        """
        reads query for all tables
        this is redundant... because it gets automapped..

        """
        db = self.app.database
        p = queries / "get.sql"
        sql = open(p, "r").read()
        tags = db.exec_query(sql)
        res = tags.to_json(orient="records")

        return JSONResponse(json.loads(res))

    def default_tags(self):
        """Checks if there are any tags, if none, inserts some defualts"""
        f = fixtures / "default-tags.sql"

        db = self.app.database
        tags = db.model.tags_tag
        q = db.session.query(tags).all()
        if len(q) == 0:
            db.exec_sql(f)

    def on_api_initialized_v2(self, api):

        # Initialize tag data if none
        self.default_tags()
        api.mount("/tags",TagsEditsRouter, name=TagsEdits.name)