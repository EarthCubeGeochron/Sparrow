import asyncio
import typing
from asyncio import sleep, get_event_loop, gather, create_task, wait
from threading import Thread
from asyncio.events import AbstractEventLoop
from json import loads
import time
import sys
from click import command, echo
from sparrow.context import get_sparrow_app
from starlette.responses import JSONResponse
from sparrow.plugins import SparrowCorePlugin
from starlette.endpoints import WebSocketEndpoint
from contextlib import redirect_stdout
from click._compat import _force_correct_text_writer
from starlette.concurrency import run_until_first_complete
from sparrow_worker import background_task
from broadcaster import Broadcast
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute
from sparrow_utils import get_logger
from .importer import WebSocketLogger

started = False

log = get_logger(__name__)


async def test_import(session, loop):
    for i in range(5):
        await sleep(1)
        await session.send_json({"text": "Hello"})
    # for i in range(5):
    #     time.sleep(1)
    #     print("Hello")
    #     loop.run_until_complete(session.send_json({"text": "Hello"}))


class ImporterEndpoint(WebSocketEndpoint):
    counter = 0
    encoding = "json"
    is_running = False
    task = None

    def get_importer(self, session):
        name = session.path_params["pipeline"]
        plugin = get_sparrow_app().plugins.get("import-tracker")
        return plugin.pipelines[name]

    def get_loop(self):
        plugin = get_sparrow_app().plugins.get("import-tracker")
        return plugin.loop

    async def on_receive(self, session, message):
        log.debug(f"Received message {message}")
        action = message.get("action", None)
        if action == "start":
            task = background_task.delay(5, 5)
            self.task = task
            print("Starting importer")
            # print(task.id)
            message["task_id"] = task.id
        if action == "stop" and self.task is not None:
            # print("Stopping importer")
            self.task.revoke()
            pass
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

        tasks = [self.send_periodically(session), self.listen(session)]
        create_task(wait(tasks))
        # self.send_periodically(session)
        # loop = get_event_loop()
        # counter = create_task(self.send_periodically(session))

    async def listen(self, session):
        plugin = get_sparrow_app().plugins.get("import-tracker")
        while True:
            await session.send_json({"text": f"Trying to connect"})
            await plugin.broadcast.connect()
            try:
                async with plugin.broadcast.subscribe(
                    channel="task:background_task:progress"
                ) as subscriber:
                    async for event in subscriber:
                        await session.send_json({"text": event.message})
                    await session.send_json({"text": f"Closing subscription"})
            except Exception as exc:
                await session.send_json({"text": str(exc)})
            await sleep(1)

    async def send_periodically(self, session):
        while True:
            await session.send_json({"text": f"Hello, planet {self.counter}!"})
            await sleep(5)
            self.counter += 1

    async def websocket_import(self, session):
        importer = self.get_importer(session)
        importer.run_loop = self.get_loop()
        await importer.import_data()


class ImportTrackerPlugin(SparrowCorePlugin):
    name = "import-tracker"
    _loop = None

    pipelines = {"test": None}
    broadcast = None

    def register_pipeline(self, name, importer):
        self.pipelines[name] = importer

    @property
    def loop(self):
        if self._loop is None:
            self._loop = get_event_loop()
        return self._loop

    async def connect(self):
        log.debug("Setting up Redis connection")
        # await self.broadcast.connect()

    def on_api_initialized_v2(self, api):
        def import_pipelines(req):
            return JSONResponse(list(self.pipelines.keys()))

        # This breaks silently if we can't connect
        self.broadcast = Broadcast("redis://broker:6379")
        log.debug("Setting up pipelines API")

        app = Starlette(
            routes=[
                Route("/pipelines", import_pipelines),
                WebSocketRoute(
                    "/pipeline/{pipeline}", ImporterEndpoint, name="import_tracker_api"
                ),
            ],
            on_startup=[self.connect],
            on_shutdown=[self.broadcast.disconnect],
        )

        api.mount("/import-tracker", app)

    async def long_runner(self):
        while True:
            await sleep(1)

    def on_setup_cli(self, cli):
        @command(name="cancel-tasks")
        def cancel_tasks():
            """Cancel import tasks"""
            for task in asyncio.Task.all_tasks(loop=self.loop):
                print(task)
                task.cancel()

        cli.add_command(cancel_tasks)
