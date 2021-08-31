from sparrow.plugins import SparrowCorePlugin
from sparrow.context import app_context
from sparrow.util import relative_path
from starlette.routing import Route, Router
from starlette.responses import JSONResponse
import sparrow
from sparrow.task_manager.base import task
import pandas as pd
from pathlib import Path
import json

from .base import OpenSearchAPI

here = Path(__file__).parent
fixtures = here / "fixtures"
procedures = here / "procedures"


class OpenSearch(SparrowCorePlugin):

    name = "open-search"
    dependencies = ["versioning"]

    def initialize_tables(self, db, refresh=True):
        initialization_fn = procedures / "on-initialization.sql"
        if refresh:
            db.exec_sql(procedures / "drop-tables.sql")

        filenames = list(fixtures.glob("*.sql"))
        filenames.sort()

        # creates tables, functions, triggers and indexes
        for fn in filenames:
            db.exec_sql(fn)

        # checks if tables are empty, if so try to fill with info from other tables
        db.exec_sql(initialization_fn)

    def on_core_tables_initialized(self, db):
        """Initialize tables on sparrow init"""
        self.initialize_tables(db)

    def on_api_initialized_v2(self, api):
        api.mount("/search", OpenSearchAPI, name=self.name)


@task(name="refresh-search-index")
def refresh_search_triggers():
    """Refresh open search triggers in case they get out of sync."""
    db = sparrow.get_database()
    open_search = sparrow.get_plugin("open-search")
    open_search.initialize_tables(db)
