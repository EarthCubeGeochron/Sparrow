from sparrow.plugins import SparrowCorePlugin
from sparrow.context import app_context
from sparrow.util import relative_path
from starlette.routing import Route, Router
from starlette.responses import JSONResponse
import pandas as pd
from pathlib import Path
import json

from .base import Open_Search_API

class OpenSearch(SparrowCorePlugin):

    name = "Open Search"
    
    def on_api_initialized_v2(self, api):
        api.mount("", Open_Search_API, name=self.name)

