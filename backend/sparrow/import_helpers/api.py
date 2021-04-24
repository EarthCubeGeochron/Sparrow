from starlette.websockets import WebSocket
from asyncio import sleep
from sparrow.plugins import SparrowCorePlugin


async def app(scope, receive, send):
    websocket = WebSocket(scope=scope, receive=receive, send=send)
    await websocket.accept()
    counter = 0
    while True:
        await websocket.send_text(f"Hello, planet {counter}!")
        await sleep(2)
        counter += 1
    await websocket.close()


class ImportTrackerPlugin(SparrowCorePlugin):
    name = "import-tracker"

    def on_api_initialized_v2(self, api):
        api.mount(
            "/import-tracker", app, name="import_tracker_api", help="Websocket server from tracking import process"
        )
