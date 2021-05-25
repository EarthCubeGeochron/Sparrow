from asyncio import sleep

from starlette.responses import JSONResponse
from sparrow.plugins import SparrowCorePlugin
from starlette.endpoints import WebSocketEndpoint

started = False


class ImporterEndpoint(WebSocketEndpoint):
    counter = 0
    encoding = "json"
    pipeline = None
    is_running = False

    async def on_receive(self, session, data):
        await session.send_text(f"Message text: {data}")

    async def on_connect(self, session):
        self.pipeline = session.path_params["pipeline"]

        await session.accept()
        await session.send_text("Bienvenue sur le websocket!")
        await self.send_periodically(session, 5)

    async def send_periodically(self, session, timer):
        while True:
            await session.send_text(f"Hello, planet {self.counter}!")
            await sleep(1)
            self.counter += 1


class ImportTrackerPlugin(SparrowCorePlugin):
    name = "import-tracker"

    pipelines = {}

    def register_pipeline(self, name, importer):
        self.pipelines[name] = importer

    def on_api_initialized_v2(self, api):
        def import_pipelines(req):
            return JSONResponse(list(self.pipelines.keys()))

        api.add_route("/import-tracker/pipelines", import_pipelines)

        api.add_websocket_route(
            "/import-tracker/pipeline/{pipeline}",
            ImporterEndpoint,
            name="import_tracker_api",
            # help="Websocket server from tracking import process",
        )
