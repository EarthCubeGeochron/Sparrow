from asyncio import sleep

from starlette.responses import JSONResponse
from sparrow.plugins import SparrowCorePlugin

started = False


async def websocket_route(session):
    pipeline = session.path_params["pipeline"]

    await session.accept()

    if not started:
        res = await session.receive_json()
        if res["action"] != "start":
            return

    counter = 1
    while True:
        await session.send_text(f"Hello, planet {counter}!")
        await sleep(1)
        counter += 1
    await session.close()


class ImportTrackerPlugin(SparrowCorePlugin):
    name = "import-tracker"

    pipelines = {}

    def register_pipeline(self, name, importer):
        self.pipelines[name] = importer

    def on_api_initialized_v2(self, api):
        def import_pipelines(req):
            return JSONResponse(self.pipelines.keys())

        api.add_route("/import-tracker/pipelines", import_pipelines)

        api.add_websocket_route(
            "/import-tracker/{pipeline}",
            websocket_route,
            name="import_tracker_api",
            # help="Websocket server from tracking import process",
        )
