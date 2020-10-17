import yaml
import json
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse, Response
from starlette.exceptions import HTTPException
from sparrow.logs import get_logger
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from collections import defaultdict
from starlette_apispec import APISpecSchemaGenerator
from ..database.mapper.util import classname_for_table
from .endpoint import ModelAPIEndpoint, model_description

log = get_logger(__name__)


async def http_exception(request, exc):
    log.error(f"{exc.status_code} {exc.detail}")
    # if exc.detail == "Internal Server Error":
    log.exception(exc)
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
        routes = {}
        for k, v in request.app.route_descriptions.items():
            desc = {d["route"]: d["description"] for d in v}
            routes[k] = desc
        return JSONResponse({"routes": routes})


def schema(request):
    s = request.app.spec.to_dict()
    return JSONResponse(s)
    # return OpenAPIResponse(s)


class APIv2(Starlette):
    """
    API v2 based on Starlette
    """

    def __init__(self, app):
        self._app = app
        self.route_descriptions = defaultdict(list)

        super().__init__(exception_handlers=exception_handlers, debug=True)
        self.spec = APISpec(
            title="Sparrow API",
            version="2.0",
            openapi_version="3.0.0",
            info={"description": "An API for accessing geochemical data"},
            plugins=[MarshmallowPlugin()],
        )

        self._add_routes()
        self._app.run_hook("api-initialized-v2", self)

    def add_schema_route(self):
        # We will want to layer this back in eventually
        # self._schemas = APISpecSchemaGenerator(self.spec)
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

        table = iface.opts.model.__table__
        # Schema-qualified name
        _schema_name = classname_for_table(table)
        root_route = table.schema or "models"
        name = table.name

        cls = type(_schema_name + "_route", (ModelAPIEndpoint,), {"Meta": Meta})
        endpoint = f"/{root_route}/{name}"

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
        desc = model_description(iface)
        basic_info = dict(
            route=endpoint,
            table=tbl.name,
            schema=tbl.schema,
            description=str(desc),
        )
        self.route_descriptions[root_route].append(basic_info)
