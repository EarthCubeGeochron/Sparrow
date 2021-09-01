from asyncio import sleep, create_task
from json import loads
from starlette.authentication import requires, AuthenticationError
from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Route, WebSocketRoute
from starlette import status

from sparrow.api import APIResponse
from sparrow.context import get_plugin
from sparrow_utils import get_logger
from sparrow.auth import get_scopes

log = get_logger(__name__)


class TaskEndpoint(WebSocketEndpoint):
    counter = 0
    encoding = "json"
    _running_task = None
    _listener = None

    def start_task(self, name: str, params: object = {}):
        log.debug("Starting task " + name)
        mgr = get_plugin("task-manager")
        task = mgr.get_task(name)
        i = mgr.celery.control.inspect()
        availability = i.ping()
        log.debug(availability)
        assert availability is not None
        self._running_task = task.delay(**params)
        log.debug(self._running_task)
        log.debug(f"Started task with id {self._running_task.id}")
        return self._running_task

    async def on_receive(self, session, message):
        action = message.get("action", None)
        task_name = session.path_params["task"]
        log.debug(f"Received message {message} for task {task_name}")

        if action == "start":
            try:
                params = message.get("params", {})
                self.start_task(task_name, params)
            except Exception as exc:
                await session.send_json({"text": str(exc)})
        if action == "stop" and self._running_task is not None:
            log.debug(f"Stopping task with id {self._running_task.id}")
            self._running_task.revoke(terminate=True)
        await session.send_json(message)
        log.debug(f"Sent message {message}")

    async def on_disconnect(self, session, close_code):
        if self._listener is not None:
            self._listener.cancel()

    async def on_connect(self, session):
        scopes = await get_scopes(session)
        if "admin" not in scopes:
            await session.close(status.WS_1008_POLICY_VIOLATION)
            return
        await session.accept()
        await session.send_json({"info": "Bienvenue sur le websocket!"})
        await self.start_listener(session)

    async def start_listener(self, session):
        if self._listener is not None:
            self._listener.cancel()
        self._listener = create_task(self.listen(session))

    async def _subscriber_loop(self, session, channel_name):
        plugin = get_plugin("task-manager")
        if plugin.broadcast is None:
            return

        await session.send_json(
            {"info": f"Trying to connect to channel {channel_name}"}
        )
        if not hasattr(plugin.broadcast._backend, "_subscriber"):
            await plugin.broadcast.connect()
        async with plugin.broadcast.subscribe(channel=channel_name) as subscriber:
            await session.send_json({"info": f"Subscribed to channel {channel_name}"})
            async for event in subscriber:
                await session.send_json(loads(event.message))
            await session.send_json({"info": f"Closing subscription"})

    async def listen(self, session):
        name = session.path_params["task"]
        channel_name = "sparrow:task:" + name
        while True:
            try:
                await self._subscriber_loop(session, channel_name)
            except Exception as exc:
                await session.send_json({"text": str(exc)})
            await session.send_json({"info": f"Trying to reconnect"})
            await sleep(1)


@requires("admin")
async def tasks(request):
    mgr = get_plugin("task-manager")
    return APIResponse(
        {
            "tasks": [
                {
                    "name": k,
                    "description": v["func"].__doc__.strip(),
                    "params": loads(v["params"].schema_json()),
                }
                for k, v in mgr._tasks.items()
                if not v["cli_only"]
            ],
            "enabled": mgr._task_worker_enabled,
        }
    )


def build_tasks_api(manager):
    routes = [Route("/", endpoint=tasks, methods=["GET"])]
    if manager._task_worker_enabled:
        task_socket_route = WebSocketRoute(
            "/{task}", TaskEndpoint, name="task_manager_api"
        )
        routes.append(task_socket_route)

    return Starlette(
        routes=routes,
        on_startup=[manager.broadcast.connect],
        on_shutdown=[manager.broadcast.disconnect],
    )
