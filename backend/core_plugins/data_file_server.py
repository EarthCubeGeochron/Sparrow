"""
The data file server plugin provides a way to access data files
via the Sparrow API using x-accel-redirect
"""

from macrostrat.utils import get_logger
from starlette.endpoints import HTTPEndpoint
from starlette.exceptions import HTTPException
from starlette.responses import (
    JSONResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
)

from sparrow.core import get_sparrow_app
from sparrow.core.data_files import download_location
from sparrow.core.plugins import SparrowCorePlugin

log = get_logger(__name__)


class DataFileAPI(HTTPEndpoint):
    async def get(self, request):
        # Need to lock this method down with authentication...
        uuid = request.path_params["uuid"]

        app = get_sparrow_app()
        db = app.database
        DataFile = db.model.data_file

        datafile = db.session.query(DataFile).get(uuid)
        if datafile is None:
            return JSONResponse(
                {"error": f"Data file with UUID {uuid} not found"}, status_code=404
            )

        location = download_location(datafile)
        if location is None:
            raise HTTPException(404, "Data file is not accessible")
        if "url" in location:
            return RedirectResponse(url=location["url"])

        disposition = f'attachment; filename="{datafile.basename}"'
        if "stream" in location:
            return StreamingResponse(
                location["stream"],
                media_type="application/octet-stream",
                headers={"Content-Disposition": disposition},
            )

        return Response(
            headers={
                "Content-Type": "",
                "Content-Disposition": disposition,
                "X-Accel-Redirect": location["accel_redirect"],
            }
        )


class DataFilePlugin(SparrowCorePlugin):
    name = "data-file"

    def on_api_initialized_v2(self, api):
        api.mount(
            "/data_file/{uuid}/download",
            DataFileAPI,
            name="data_file_api",
            help="Download a data file by URL",
        )
