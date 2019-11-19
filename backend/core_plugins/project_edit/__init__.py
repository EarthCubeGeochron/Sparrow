from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from sparrow.api.base import APIResourceCollection
from sparrow.plugins import SparrowCorePlugin

ProjectEditAPI = APIResourceCollection()

parser = reqparse.RequestParser()

@ProjectEditAPI.resource('/<int:id>')
class ProjectEditResource(Resource):
    @jwt_required
    def put(self, id):
        args = parser.parse_args()
        return args, 201

class ProjectEditPlugin(SparrowCorePlugin):
    name = "project-edit"
    def on_api_initialized(self, api):
        api.add_resource(ProjectEditAPI, '/edit/project')
