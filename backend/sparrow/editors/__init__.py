from os import environ
from .base import construct_edit_app, EditApi
from sparrow.plugins import SparrowCorePlugin
from ..auth.backend import JWTBackend


##app = construct_edit_app()

class DatasheetEditPlugin(SparrowCorePlugin):
    name = 'edits'

    def on_api_initialized_v2(self, api):
        api.mount("/edits", EditApi, name="edit_api")