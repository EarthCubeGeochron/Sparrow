from sparrow.plugins import SparrowCorePlugin

from flask import current_app, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from sparrow.api.base import APIResourceCollection
from sparrow.plugins import SparrowCorePlugin

parser = reqparse.RequestParser()
parser.add_argument('username',
    help='This field cannot be blank',
    required=True)
parser.add_argument('password',
    help='This field cannot be blank',
    required=True)

ProjectEditAPI = APIResourceCollection()

@ProjectEditAPI.resource('/')
class ProjectEditAPI(Resource):
    @jwt_required
    def post(self):
        return "Hello from stuff."

class ProjectEditPlugin(SparrowCorePlugin):
    name = "project-edit"
    def on_api_initialized(self, api):
        api.add_resource(ProjectEditAPI, '/edit/project')
