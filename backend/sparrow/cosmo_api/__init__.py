from sparrow.plugins import SparrowPlugin
from flask import Blueprint

cosmo = Blueprint('cosmo_api', __name__)

@cosmo.route('/')
def index():
    return "Hello from COSMO API"

class CosmoPlugin(SparrowPlugin):
    name = "cosmo-api"
    def on_api_initialized(self, api):
        self.app.register_blueprint(cosmo, url_prefix='/cosmo-api')
