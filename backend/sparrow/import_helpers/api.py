from asyncio import sleep
from sparrow.plugins import SparrowCorePlugin


async def websocket_route(session):
    await session.accept()
    counter = 1
    while True:
        await session.send_text(f"Hello, planet {counter}!")
        await sleep(1)
        counter += 1
    await session.close()


class ImportTrackerPlugin(SparrowCorePlugin):
    name = "import-tracker"

    def on_api_initialized_v2(self, api):
        api.add_websocket_route(
            "/import-tracker",
            websocket_route,
            name="import_tracker_api",
            # help="Websocket server from tracking import process",
        )
