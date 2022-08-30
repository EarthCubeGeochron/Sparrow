from flask import current_app
from flask_restful import Resource
from sparrow.utils import get_logger
from sparrow.core.legacy.api_v1 import (
    APIResourceCollection,
    ModelEditParser,
    get_jwt_identity,
)
from sparrow.core.plugins import SparrowCorePlugin

log = get_logger(__name__)

ProjectEditAPI = APIResourceCollection()


@ProjectEditAPI.resource("/<int:id>")
class ProjectEditResource(Resource):
    def put(self, id):
        get_jwt_identity(required=True)

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

        db.session.add(
            m
        )  ## I believe this is redudent, because you're directly editing a sqlalchemy session object
        db.session.commit()

        res = m.to_dict()
        log.debug(res)

        # We need to replace this hacky solution with marshaling with
        # marshmallow or similar
        return res, 201


class ProjectEditPlugin(SparrowCorePlugin):
    name = "project-edit"
    sparrow_version = "==3.*"

    def on_api_v1_initialized(self, api):
        api.add_resource(ProjectEditAPI, "/edit/project")
