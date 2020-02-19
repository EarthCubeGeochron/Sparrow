from flask import current_app, jsonify, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from sparrow import get_logger
from sparrow.api import APIResourceCollection, ModelEditParser
from sparrow.plugins import SparrowCorePlugin

log = get_logger(__name__)

ImportDataAPI = APIResourceCollection()

@ImportDataAPI.resource('/<string:model_name>')
class ImportDataResource(Resource):
    # We should enable authentication but that is tricky with scripts
    #@jwt_required
    def put(self, model_name):
        db = current_app.database
        req = request.get_json()
        data = req.get("data")
        res = db.load_data(model_name, data)

        return res.id, 201

class ImportDataPlugin(SparrowCorePlugin):
    name = "import-data"
    def on_api_initialized(self, api):
        api.add_resource(ImportDataAPI, '/import-data')
