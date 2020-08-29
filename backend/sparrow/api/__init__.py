import yaml
import json
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse, Response
from starlette.exceptions import HTTPException
from sparrow.logs import get_logger
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from starlette_apispec import APISpecSchemaGenerator
from ..database.mapper.util import classname_for_table
from .endpoint import ModelAPIEndpoint

log = get_logger(__name__)


async def http_exception(request, exc):
    return JSONResponse(
        {"error": {"detail": exc.detail, "status_code": exc.status_code}},
        status_code=exc.status_code,
    )


exception_handlers = {HTTPException: http_exception}


class OpenAPIResponse(Response):
    media_type = "application/vnd.oai.openapi"

    def render(self, content):
        log.info(content)
        return yaml.dump(content).encode("utf-8")


class APIEntry(HTTPEndpoint):
    async def get(self, request):
        """
        description:
            A test API base route.
        responses:
            200:
                description: It's alive!
        """
        desc = {d["route"]: d["description"] for d in request.app.route_descriptions}
        return JSONResponse({"routes": desc})


def schema(request):
    s = request.app.spec.to_dict()
    return JSONResponse(s)
    # return OpenAPIResponse(s)


class APIv2(Starlette):
    def __init__(self, app):
        self._app = app
        self.route_descriptions = []

        super().__init__(exception_handlers=exception_handlers)
        self.spec = APISpec(
            title="Sparrow API",
            version="2.0",
            openapi_version="3.0.0",
            info={"description": "An API for accessing geochemical data"},
            plugins=[MarshmallowPlugin()],
        )

        self._add_routes()

    def add_schema_route(self):
        self._schemas = APISpecSchemaGenerator(self.spec)
        self.add_route("/schema", schema, methods=["GET"], include_in_schema=False)

    def _add_routes(self):

        self.add_route("/", APIEntry)

        db = self._app.database

        for iface in db.interface:
            self._add_model_route(iface)

        self.add_schema_route()

    def _add_model_route(self, iface):
        class Meta:
            database = self._app.database
            schema = iface

        name = classname_for_table(iface.opts.model.__table__)
        cls = type(name + "_route", (ModelAPIEndpoint,), {"Meta": Meta})
        endpoint = "/" + name
        self.add_route(endpoint, cls, include_in_schema=False)
        self.add_route(endpoint + "/{id}", cls, include_in_schema=False)

        self.spec.path(
            path=endpoint,
            operations=dict(
                get=dict(
                    responses={
                        "200": {
                            "content": {"application/json": {"schema": iface.__name__}}
                        }
                    }
                )
            ),
        )

        tbl = iface.opts.model.__table__
        basic_info = dict(
            route=endpoint, table=tbl.name, schema=tbl.schema, description="A route!",
        )
        self.route_descriptions.append(basic_info)
