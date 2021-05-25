from asyncio import sleep, get_event_loop, gather, create_task, wait
from json import loads
from starlette.responses import JSONResponse
from sparrow.plugins import SparrowCorePlugin
from starlette.endpoints import WebSocketEndpoint

started = False


class ImporterEndpoint(WebSocketEndpoint):
    counter = 0
    encoding = "json"
    pipeline = None
    is_running = False
    task = None

    async def on_receive(self, session, message):
        try:
            action = message.get("action", None)
            if action == "start":
                self.task = create_task(self.send_periodically(session))
            if action == "stop" and self.task is not None:
                self.task.cancel()
            await session.send_json(message)
        except Exception as exc:
            await session.send_json({"error": str(exc)})

    async def on_connect(self, session):
        self.pipeline = session.path_params["pipeline"]

        await session.accept()
        await session.send_json({"text": "Bienvenue sur le websocket!"})
        # self.task = create_task(self.send_periodically(session))

        # loop = get_event_loop()
        # task = loop.create_task(self.send_periodically(session, 5))
        # self.send_periodically(session)
        # loop = get_event_loop()
        # counter = create_task(self.send_periodically(session))

    async def send_periodically(self, session):
        while True:
            await session.send_json({"text": f"Hello, planet {self.counter}!"})
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
