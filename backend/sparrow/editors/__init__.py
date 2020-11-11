from os import environ
from .base import construct_edit_app, EditApi
from sparrow.plugins import SparrowCorePlugin
from ..auth.backend import JWTBackend


##app = construct_edit_app()

class EditAPI(SparrowCorePlugin):
    name = 'edits'

    backend = JWTBackend(environ.get("SPARROW_SECRET_KEY", ""))

    def on_intialize_edit_api(self, api):
        api.mount("/edits", EditAPI, name="edit_api")