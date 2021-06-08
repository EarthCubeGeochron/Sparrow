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


class TagsEdits(HTTPEndpoint):
    """
    Tags endpoint for adding and removing tag relationships from models.
    SQL assisted, for a current replacement for schemas.
    """

    name = "TagsEdits"

    @requires("admin")
    async def put(self, request):
        """
        Adds a tag model relationship through sqlalchemy orm

        """
        db = app_context().database

        model_name = request.path_params["model"]

        model = getattr(db.model, model_name)
        tags = db.model.tags_tag

        data = await request.json()

        with db.session_scope():

            tag_ids = data["tag_ids"]
            model_id = data["model_id"]

            # get current model and that models tag collection
            current_model = db.session.query(model).get(model_id)
            current_collection = current_model.tags_tag_collection

            for tag_id in tag_ids:
                tag = db.session.query(tags).get(tag_id)
                current_model.tags_tag_collection = [*current_collection, tag]

                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    return JSONResponse({"Status": "Error", "message": f"cannot insert tag {tag_id}"}, status_code=404)

        return JSONResponse(
            {"Status": "Success", "tag_ids": f"{tag_ids}", "model": f"{model_name}", "model_id": f"{model_id}"}
        )


TagsEditsRouter = Router([Route("/models/{model}", endpoint=TagsEdits, methods=["PUT"])])


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
        api.mount("/tags", TagsEditsRouter, name=TagsEdits.name)
