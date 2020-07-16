from flask import current_app, jsonify, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from sparrow import get_logger
from sparrow.api import APIResourceCollection, ModelEditParser
from sparrow.plugins import SparrowCorePlugin
from marshmallow.exceptions import ValidationError
from sparrow.util import get_qualified_name

log = get_logger(__name__)

ImportDataAPI = APIResourceCollection()


def construct_error_response(err: Exception, code: int):
    """Constructs an error response for a Marshmallow validation error
    """
    try:
        # ValidationErrors have "messages" but most errors don't
        msg = err.messages
    except AttributeError:
        msg = [str(err)]

    return (
        {
            "error": {
                "type": get_qualified_name(err),
                "code": code,
                "messages": msg
                # Note: the original data *could* be packaged in the response, but
                # for now we have chosen not to do that. It seems useless to send back
                # (possibly large) datasets the client already has.
            }
        },
        code,
    )


@ImportDataAPI.resource("/<string:model_name>")
class ImportDataResource(Resource):
    # We should enable authentication but that is tricky with scripts
    # @jwt_required

    # Raises a https://marshmallow.readthedocs.io/en/stable/api_reference.html#marshmallow.exceptions.ValidationError
    # when bad data is given

    def put(self, model_name):
        db = current_app.database
        try:
            req = request.get_json()
            log.debug(req)
            data = req.get("data")
            res = db.load_data(model_name, data)
            return res.id, 201
        except Exception as err:
            return construct_error_response(err, 400)


class ImportDataPlugin(SparrowCorePlugin):
    name = "import-data"

    def on_api_initialized(self, api):
        api.add_resource(ImportDataAPI, "/import-data")
