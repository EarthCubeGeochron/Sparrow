import yaml
import json
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse, Response
from starlette.exceptions import HTTPException
from sparrow.logs import get_logger
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from collections import defaultdict
from starlette_apispec import APISpecSchemaGenerator
from ..database.mapper.util import classname_for_table
from .endpoints.selectables.data_file import DataFileListEndpoint, DataFileFilterByModelID
from .endpoints.selectables.sample import SubSamples

from .endpoints import (
    ModelAPIEndpoint,
    ViewAPIEndpoint
)

from .endpoints import ModelAPIEndpoint, ViewAPIEndpoint
from .api_info import model_description, root_example, root_info, meta_info
from .response import APIResponse
from .exceptions import SparrowAPIError
import time

log = get_logger(__name__)


async def http_exception(request, exc):
    log.error(f"{exc.status_code} {exc.detail}")
    # if exc.detail == "Internal Server Error":
    log.exception(exc)
    return JSONResponse(
        {"error": {"detail": exc.detail, "status_code": exc.status_code}},
        status_code=exc.status_code,
    )


exception_handlers = {HTTPException: http_exception, SparrowAPIError: http_exception}


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
            # We should refactor this significantly...
            if isinstance(v, str):
                routes[k] = v
            else:
                desc = {d["route"]: d["description"] for d in v}
                routes[k] = desc
        return JSONResponse(
            {**root_info(), "routes": routes, "examples": root_example()}
        )


def schema(request):
    s = request.app.spec.to_dict()
    return JSONResponse(s)
    # return OpenAPIResponse(s)


class ServerTimings(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        dur = (time.time() - start) * 1e3
        response.headers["Server-Timing"] = f"total;dur={dur}"
        return response


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

        self.add_middleware(ServerTimings)

        self._add_routes()
        self._app.run_hook("api-initialized-v2", self)

    def add_route(self, path, *args, **kwargs):
        desc = kwargs.pop("help", None)
        if desc is not None:
            self.route_descriptions[path] = desc

        super().add_route(path, *args, **kwargs)

    def mount(self, path, app, **kwargs):
        desc = kwargs.pop("help", None)
        if desc is not None:
            self.route_descriptions[path] = desc
        super().mount(path, app, **kwargs)

    def add_schema_route(self):
        # We will want to layer this back in eventually
        # self._schemas = APISpecSchemaGenerator(self.spec)
        self.add_route("/schema", schema, methods=["GET"], include_in_schema=False)

    def add_meta_route(self):
        self.add_route("/meta", JSONResponse(meta_info()), methods=["GET"])

    def _add_routes(self):

        self.add_route("/", APIEntry)

        db = self._app.database

        skip_list = [db.interface.user]
        for iface in db.interface:
            if iface in skip_list:
                continue
            self._add_model_route(iface)

        self.add_view_route(
            "authority",
            schema="vocabulary",
            description="Route to view authorities for technical descriptions",
        )
        self.add_view_route(
            "age_context", description="Ages directly connected to geologic context"
        )

        self.add_schema_route()
        self.add_meta_route()
        self.add_route("/data_file/list", DataFileListEndpoint)
        self.add_route("/data_file/filter", DataFileFilterByModelID)
        self.add_route("/sub-sample/{id}", SubSamples, methods=['GET'])

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
            route=endpoint, table=tbl.name, schema=tbl.schema, description=str(desc)
        )
        self.route_descriptions[root_route].append(basic_info)

    def add_view_route(self, tablename, schema="core_view", description=""):
        _tbl = self._app.database.mapper.reflect_table(tablename, schema=schema)

        class Meta:
            table = _tbl

        name = _tbl.name
        cls = type(name + "_route", (ViewAPIEndpoint,), {"Meta": Meta})
        root_route = schema
        endpoint = f"/{root_route}/{name}"

        self.add_route(endpoint, cls, include_in_schema=False)

        basic_info = dict(
            route=endpoint, table=_tbl.name, schema=schema, description=description
        )
        self.route_descriptions[root_route].append(basic_info)
