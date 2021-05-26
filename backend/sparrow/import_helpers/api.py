import asyncio
import typing
from asyncio import sleep, get_event_loop, gather, create_task, wait
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

from .importer import WebSocketLogger

started = False


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
        importer = self.get_importer(session)
        loop = self.get_loop()
        try:
            action = message.get("action", None)
            if action == "start" and importer._task is None:
                print("Starting importer")
                importer.websocket = session
                importer._task = loop.create_task(self.websocket_import(session))
                print(importer._task)
            if action == "stop" and importer._task is not None:
                print("Stopping importer")
                importer._task.cancel()
                print(importer._task)
            await session.send_json(message)
        except Exception as exc:
            print(exc)
            await session.send_json({"error": str(exc)})

    async def on_connect(self, session):
        await session.accept()
        await session.send_json({"text": "Bienvenue sur le websocket!"})

        importer = self.get_importer(session)
        importer.websocket = session
        # self.task = create_task(self.send_periodically(session))

        # loop = get_event_loop()
        # task = loop.create_task(self.send_periodically(session, 5))
        # self.send_periodically(session)
        # loop = get_event_loop()
        # counter = create_task(self.send_periodically(session))

    async def send_periodically(self, session):
        while True:
            print(f"Hello, planet {self.counter}!")
            # await session.send_json({"text": f"Hello, planet {self.counter}!"})
            await sleep(1)
            self.counter += 1

    async def websocket_import(self, session):
        importer = self.get_importer(session)
        importer.run_loop = self.get_loop()
        await importer.import_data()


class ImportTrackerPlugin(SparrowCorePlugin):
    name = "import-tracker"
    _loop = None

    pipelines = {}

    def register_pipeline(self, name, importer):
        self.pipelines[name] = importer

    @property
    def loop(self):
        if self._loop is None:
            self._loop = get_event_loop()
        return self._loop

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
