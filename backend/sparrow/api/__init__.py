from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from sparrow.logs import get_logger
from ..database.mapper.util import classname_for_table
from .schema import schema
from .endpoint import APIEndpoint

log = get_logger(__name__)


async def http_exception(request, exc):
    return JSONResponse(
        {"error": {"detail": exc.detail, "status_code": exc.status_code}},
        status_code=exc.status_code,
    )


exception_handlers = {HTTPException: http_exception}


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


class APIv2(Starlette):
    def __init__(self, app):
        self._app = app
        self.route_descriptions = []
        api_args = dict(
            title="Sparrow API",
            version="2.0",
            description="An API for accessing geochemical data",
        )
        super().__init__(exception_handlers=exception_handlers)
        self._add_routes()

    def _add_routes(self):

        self.add_route("/", APIEntry)

        db = self._app.database

        for iface in db.interface:
            self._add_schema_route(iface)

        self.add_route("/schema", schema, methods=["GET"], include_in_schema=False)

    def _add_schema_route(self, iface):
        class Meta:
            database = self._app.database
            schema = iface

        name = classname_for_table(iface.opts.model.__table__)
        cls = type(name + "_route", (APIEndpoint,), {"Meta": Meta})
        endpoint = "/" + name
        self.add_route(endpoint, cls)

        tbl = iface.opts.model.__table__
        basic_info = dict(
            route=endpoint, table=tbl.name, schema=tbl.schema, description="A route!",
        )
        self.route_descriptions.append(basic_info)
