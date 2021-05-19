from sparrow.plugins import SparrowCorePlugin
from sparrow.context import app_context
from sparrow.util import relative_path
from starlette.routing import Route, Router
from starlette.responses import JSONResponse
import pandas as pd
from pathlib import Path
import json

from .base import Open_Search_API

here = Path(__file__).parent
fixtures = here / "fixtures"
procedures = here / "procedures"


class OpenSearch(SparrowCorePlugin):

    name = "Open Search"

    def on_database_ready(self, db):
        # initialization_fn = procedures / "on-initialization.sql"

        filenames = list(fixtures.glob("*.sql"))
        filenames.sort()

        for fn in filenames:
            db.exec_sql(fn)

        # db.exec_sql(initialization_fn)

    def on_api_initialized_v2(self, api):
        api.mount("", Open_Search_API, name=self.name)
