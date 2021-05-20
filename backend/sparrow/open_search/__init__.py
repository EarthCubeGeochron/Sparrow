from sparrow.plugins import SparrowCorePlugin
from sparrow.context import app_context
from sparrow.util import relative_path
from starlette.routing import Route, Router
from starlette.responses import JSONResponse
import pandas as pd
from pathlib import Path
import json

from .base import OpenSearchAPI

here = Path(__file__).parent
fixtures = here / "fixtures"
procedures = here / "procedures"


class OpenSearch(SparrowCorePlugin):

    name = "open-search"

    def initialize_tables(self, db):
        initialization_fn = procedures / "on-initialization.sql"

        filenames = list(fixtures.glob("*.sql"))
        filenames.sort()

        # creates tables, functions, triggers and indexes
        for fn in filenames:
            db.exec_sql(fn)

        # checks if tables are empty, if so try to fill with info from other tables
        db.exec_sql(initialization_fn)

    def on_database_ready(self, db):
        """"Initialize tables on database ready"""
        self.initialize_tables(db)
      
    def on_core_tables_initialized(self, db):
        """Initialize tables on sparrow init"""
        self.initialize_tables(db)

    def on_api_initialized_v2(self, api):
        api.mount("/search", OpenSearchAPI, name=self.name)
