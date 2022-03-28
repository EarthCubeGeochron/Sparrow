from starlette.endpoints import WebSocketEndpoint
from sparrow.plugins import SparrowCorePlugin
from sparrow.utils import get_logger

log = get_logger(__name__)


class Heartbeat(WebSocketEndpoint):
    async def send_ok(self, session):
        await session.send_json({"status": "ok"})

    async def on_receive(self, session):
        log.info("Received ping")
        await self.send_ok(session)


class HeartbeatPlugin(SparrowCorePlugin):
    name = "heartbeat"
    dependencies = ["api-v2"]

    def on_api_initialized_v2(self, api):
        api.add_websocket_route("/heartbeat", Heartbeat)
