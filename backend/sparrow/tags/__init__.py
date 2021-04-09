from sparrow.plugins import SparrowCorePlugin
from starlette.responses import JSONResponse
from pathlib import Path
from sparrow.util import relative_path
import json


here = Path(__file__).parent
fixtures = here / "fixtures"
queries = here / "queries"


class Tags(SparrowCorePlugin):
    """
    Tags implementation, create a new database schema and tables.
    And create API routes, get,post, and delete

    These routes are specific to the tag model only.. the relationship
    will show up in those respective models
    """

    name = "tags"

    ## database-available hook is before the automapper
    def on_database_available(self, db):
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