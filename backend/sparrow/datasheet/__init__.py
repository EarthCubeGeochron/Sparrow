from os import environ
from .base import Datasheet_Api
from sparrow.plugins import SparrowCorePlugin
from ..auth.backend import JWTBackend


class DatasheetPlugin(SparrowCorePlugin):
    name = 'datasheet'

    def on_api_initialized_v2(self, api):
        api.mount("/datasheet", Datasheet_Api, name="datasheet_api")