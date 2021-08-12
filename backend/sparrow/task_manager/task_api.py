from sparrow.api import APIResponse
from sparrow.context import get_plugin
from starlette.routing import Route, Router
from starlette.authentication import requires
from asyncio import sleep, create_task
from json import loads
from sparrow.context import get_plugin
from starlette.endpoints import WebSocketEndpoint
from sparrow_worker import import_task
from starlette.routing import Route, WebSocketRoute
from sparrow_utils import get_logger

started = False

log = get_logger(__name__)


class TaskEndpoint(WebSocketEndpoint):
    counter = 0
    encoding = "json"
    is_running = False
    task = None

    def get_importer(self, session):
        name = session.path_params["pipeline"]
        plugin = get_plugin("import-tracker")
        return plugin.pipelines[name]

    def get_loop(self):
        plugin = get_plugin("import-tracker")
        return plugin.loop

    async def on_receive(self, session, message):

        log.debug(f"Received message {message}")
        action = message.get("action", None)
        name = session.path_params["pipeline"]

        if action == "start":
            try:

                def on_message(body):
                    log.info("Message: " + body)
                    create_task(session.send_json({"text": body}))

                log.info("Starting task")
                task = import_task.delay(name)
                # task.get(on_message=on_message, propagate=False)
                self.task = task

                # print(task.id)
                message["task_id"] = task.id
            except Exception as exc:
                await session.send_json({"text": str(exc)})
        if action == "stop" and self.task is not None:
            # print("Stopping importer")
            self.task.revoke(terminate=True)
        await session.send_json(message)

    async def on_disconnect(self, session):
        pass
        # importer = self.get_importer(session)
        # if importer._task is not None:
        #     importer._task.cancel()

    async def on_connect(self, session):
        await session.accept()
        await session.send_json({"text": "Bienvenue sur le websocket!"})

        # await run_until_first_complete(
        #     (self.listen, {"session": session}),
        #     (self.send_periodically, {"session": session}),
        # )

        # importer = self.get_importer(session)
        # importer.websocket = session
        # self.task = create_task()

        create_task(self.listen(session))
        # self.send_periodically(session)
        # loop = get_event_loop()
        # counter = create_task(self.send_periodically(session))

    async def listen(self, session):
        plugin = get_plugin("task-manager")
        name = session.path_params["task"]
        while True:
            await session.send_json({"text": f"Trying to connect"})
            await plugin.broadcast.connect()
            try:
                async with plugin.broadcast.subscribe(
                    channel="sparrow:task:" + name
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
        [{"name": k, "description": v.__doc__.strip()} for k, v in mgr._tasks.items()]
    )


TasksAPI = Router(
    [
        Route("/", endpoint=tasks, methods=["GET"]),
        WebSocketRoute("/{task}", TaskEndpoint, name="task_manager_api"),
    ]
)
