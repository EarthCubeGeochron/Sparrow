from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse, Response
from sparrow.core.context import app_context
from sparrow.logs import get_logger
from sparrow.core.plugins import SparrowCorePlugin
from starlette.routing import Route, Router
from starlette.authentication import requires

from sparrow.core.util import get_qualified_name

log = get_logger(__name__)


def construct_error_response(err: Exception, code: int):
    """Constructs an error response for a Marshmallow validation error"""
    try:
        # ValidationErrors have "messages" but most errors don't
        msg = err.messages
    except AttributeError:
        msg = [str(err)]

    return JSONResponse(
        content={
            "error": {
                "type": get_qualified_name(err),
                "code": code,
                "messages": msg
                # Note: the original data *could* be packaged in the response, but
                # for now we have chosen not to do that. It seems useless to send back
                # (possibly large) datasets the client already has.
            }
        },
        status_code=code,
    )


class ImportData(HTTPEndpoint):

    # http://localhost:5002/api/v2/import-data/models/{model_name}

    # Raises a https://marshmallow.readthedocs.io/en/stable/api_reference.html#marshmallow.exceptions.ValidationError
    # when bad data is given

    @requires("admin")
    async def put(self, request):
        db = app_context().database
        try:
            model_name = request.path_params["model_name"]

            req = await request.json()
            data = req["data"]
            log.debug(data)
            res = db.load_data(model_name, data)

            return JSONResponse(
                {"status": "success", "model": f"{model_name}", "id": res.id}
            )
        except Exception as err:
            return construct_error_response(err, 400)

    async def get(self, request):
        model_name = request.path_params["model_name"]

        return JSONResponse({"Model": f"{model_name}"})


ImportDataAPI = Router(
    [Route("/models/{model_name}", endpoint=ImportData, methods=["PUT", "GET"])]
)


class ImportDataPlugin(SparrowCorePlugin):
    name = "import-data"
    sparrow_version = "==3.*"

    def on_api_initialized_v2(self, api):
        api.mount("/import-data", ImportDataAPI, name=self.name)
