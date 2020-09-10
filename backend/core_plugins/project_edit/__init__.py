from flask import current_app, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from sparrow import get_logger
from sparrow.api.v1 import APIResourceCollection, ModelEditParser
from sparrow.plugins import SparrowCorePlugin

log = get_logger(__name__)

ProjectEditAPI = APIResourceCollection()


@ProjectEditAPI.resource("/<int:id>")
class ProjectEditResource(Resource):
    @jwt_required
    def put(self, id):

        db = current_app.database
        model = db.model.project

        # Could potentially improve database getting
        parser = ModelEditParser(model)
        args = parser.parse_args()

        log.debug(args)

        m = db.session.query(model).get(id)
        # We don't do any error handling right now
        for k, v in args.items():
            setattr(m, k, v)

        db.session.add(m)
        db.session.commit()

        res = m.to_dict()
        log.debug(res)

        # We need to replace this hacky solution with marshaling with
        # marshmallow or similar
        return res, 201


class ProjectEditPlugin(SparrowCorePlugin):
    name = "project-edit"

    def on_api_initialized(self, api):
        api.add_resource(ProjectEditAPI, "/edit/project")
