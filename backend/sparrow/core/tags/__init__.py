import json
from pathlib import Path

from macrostrat.schema_management import SchemaDefinition
from starlette.authentication import requires
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from starlette.routing import Route, Router

from sparrow.core.context import app_context
from sparrow.core.plugins import SparrowCorePlugin

here = Path(__file__).parent
fixtures = here / "fixtures"


class Tags(SparrowCorePlugin):
    """
    Tags implementation, create a new database schema and tables.
    And create API routes, get,post, and delete

    These routes are specific to the tag model only.. the relationship
    will show up in those respective models
    """

    name = "tags"

    def on_define_schema(self, chunks):
        """Schema and tables for tags"""
        chunks.append(
            SchemaDefinition(
                name="tags", depends_on=["core"], provides=[fixtures / "tags.sql"]
            )
        )

    def default_tags(self):
        """Checks if there are any tags, if none, inserts some defualts"""
        f = fixtures / "default-tags.sql"

        db = self.app.database
        tags = db.model.tags_tag
        q = db.session.query(tags).all()
        if len(q) == 0:
            db.run_sql(f)

    def on_database_ready(self, db):
        # A new lab starts with a few tags
        self.default_tags()
