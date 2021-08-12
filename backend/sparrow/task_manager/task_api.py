from sparrow.api import APIResponse
from sparrow.context import get_plugin
from starlette.routing import Route, Router
from starlette.authentication import requires
from asyncio import sleep, create_task
from json import loads
from sparrow.context import get_plugin
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Route, WebSocketRoute
from sparrow_utils import get_logger
from starlette.applications import Starlette

log = get_logger(__name__)


class TaskEndpoint(WebSocketEndpoint):
    counter = 0
    encoding = "json"
    _running_task = None
    _listener = None

    def start_task(self, name: str):
        log.debug("Starting task " + name)
        mgr = get_plugin("task-manager")
        task = mgr.get_task(name)
        i = mgr.celery.control.inspect()
        availability = i.ping()
        log.debug(availability)
        assert availability is not None
        kwargs = {}
        if name == "location-names":
            kwargs = dict(overwrite=True)
        self._running_task = task.delay(**kwargs)
        log.debug(self._running_task)
        log.debug(f"Started task with id {self._running_task.id}")
        return self._running_task

    async def on_receive(self, session, message):

        action = message.get("action", None)
        task_name = session.path_params["task"]
        log.debug(f"Received message {message} for task {task_name}")

        if action == "start":
            try:
                self.start_task(task_name)
            except Exception as exc:
                await session.send_json({"text": str(exc)})
        if action == "stop" and self._running_task is not None:
            # print("Stopping importer")
            self._running_task.revoke(terminate=True)
        await session.send_json(message)
        log.debug(f"Sent message {message}")

    async def on_disconnect(self, session):
        if self._listener is not None:
            self._listener.cancel()

    async def on_connect(self, session):
        await session.accept()
        await session.send_json({"text": "Bienvenue sur le websocket!"})
        await self.start_listener(session)

    async def start_listener(self, session):
        if self._listener is not None:
            self._listener.cancel()
        self._listener = create_task(self.listen(session))

    async def listen(self, session):
        plugin = get_plugin("task-manager")
        name = session.path_params["task"]
        channel_name = "sparrow:task:" + name
        while True:
            if plugin.broadcast is not None:
                await session.send_json(
                    {"text": f"Trying to connect to channel {channel_name}"}
                )
                if not hasattr(plugin.broadcast._backend, "_subscriber"):
                    await plugin.broadcast.connect()
                try:
                    async with plugin.broadcast.subscribe(
                        channel=channel_name
                    ) as subscriber:
                        await session.send_json(
                            {"text": f"Subscribed to channel {channel_name}"}
                        )
                        async for event in subscriber:
                            await session.send_json(loads(event.message))
                        await session.send_json({"text": f"Closing subscription"})
                except Exception as exc:
                    await session.send_json({"text": str(exc)})
            await session.send_json({"text": f"Trying to reconnect"})
            await sleep(1)

    async def send_periodically(self, session):
        while True:
            await session.send_json({"text": f"Hello, planet {self.counter}!"})
            await sleep(5)
            self.counter += 1


@requires("admin")
async def tasks(request):
    mgr = get_plugin("task-manager")
    return APIResponse(
        [
            {"name": k, "description": v.__doc__.strip()}
            for k, v in mgr._celery_tasks.items()
        ]
    )


def build_tasks_api(manager):
    return Starlette(
        routes=[
            Route("/", endpoint=tasks, methods=["GET"]),
            WebSocketRoute("/{task}", TaskEndpoint, name="task_manager_api"),
        ],
        on_startup=[manager.broadcast.connect],
        on_shutdown=[manager.broadcast.disconnect],
    )
