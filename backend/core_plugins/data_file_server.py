"""
The data file server plugin provides a way to access data files
via the Sparrow API using x-accel-redirect
"""

import os
from starlette.endpoints import HTTPEndpoint
from starlette.responses import RedirectResponse, JSONResponse, Response
from sparrow.plugins import SparrowCorePlugin
from sparrow.context import get_sparrow_app
from starlette.exceptions import HTTPException
from sparrow_utils import get_logger

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

        key = datafile.file_path

        try:
            cloud_data = app.plugins.get("cloud-data")
            url = cloud_data.get_download_url(key)
            log.debug("Redirecting to cloud download url")
            return RedirectResponse(url=url)
        except AttributeError:
            pass

        if "SPARROW_DATA_DIR" not in os.environ:
            raise HTTPException(404, "Data directory not accessible")

        return Response(
            headers={
                "Content-Type": "",
                "Content-Disposition": f'attachment; filename="{datafile.basename}"',
                # X-Accel-Redirect is an NGINX feature, if we're running sparrow outside of
                # the usual docker context it will not work...
                # Right now, the SPARROW_DATA_DIR folder is always mounted to /data in Docker...
                "X-Accel-Redirect": f"/data/{key}",
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
