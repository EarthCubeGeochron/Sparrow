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

log = get_logger(__name__)


class TaskEndpoint(WebSocketEndpoint):
    counter = 0
    encoding = "json"

    def start_task(self, name: str):
        log.debug("Starting task " + name)
        mgr = get_plugin("task-manager")
        task = mgr.get_task(name)
        i = mgr.celery.control.inspect()
        availability = i.ping()
        log.debug(availability)
        assert availability is not None
        res = task.delay()
        log.debug(res)
        log.debug(f"Started task with id {res.id}")
        return res

    async def on_receive(self, session, message):

        action = message.get("action", None)
        task_name = session.path_params["task"]
        log.debug(f"Received message {message} for task {task_name}")

        if action == "start":
            try:
                self.start_task(task_name)
            except Exception as exc:
                await session.send_json({"text": str(exc)})
        if action == "stop":
            pass
        await session.send_json(message)
        log.debug(f"Sent message {message}")

    async def on_disconnect(self, session):
        pass
        # importer = self.get_importer(session)
        # if importer._task is not None:
        #     importer._task.cancel()

    async def on_connect(self, session):
        await session.accept()
        await session.send_json({"text": "Bienvenue sur le websocket!"})
        create_task(self.listen(session))

    async def listen(self, session):
        plugin = get_plugin("task-manager")
        name = session.path_params["task"]
        channel_name = "sparrow:task:" + name
        while True:
            await session.send_json(
                {"text": f"Trying to connect to channel {channel_name}"}
            )
            await plugin.broadcast.connect()
            try:
                async with plugin.broadcast.subscribe(
                    channel=channel_name
                ) as subscriber:
                    async for event in subscriber:
                        await session.send_json(loads(event.message))
                    await session.send_json({"text": f"Closing subscription"})
            except Exception as exc:
                await session.send_json({"text": str(exc)})
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


TasksAPI = Router(
    [
        Route("/", endpoint=tasks, methods=["GET"]),
        WebSocketRoute("/{task}", TaskEndpoint, name="task_manager_api"),
    ]
)
