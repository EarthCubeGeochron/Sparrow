"""
Sparrow's task manager provides a way to run long-running processes
(e.g., imports), within the context of a Sparrow application.

Tasks have

- Unique names
- Autogenerated command-line applications (if desired)
- Celery task representation
- Optional stdout redirection

"""
from celery import Celery
from sparrow.logs import get_logger
from os import environ
from json import loads
from sparrow.plugins import SparrowCorePlugin
from sparrow.settings import TASK_BROKER, TASK_WORKER_ENABLED
import typer
from .task_api import build_tasks_api
from .base import (
    create_args_schema,
    task,  # noqa
    _tasks_to_register,
    _name_for_task,
    SparrowTaskError,
)
from redis import Redis
from broadcaster import Broadcast


log = get_logger(__name__)


class SparrowTaskManager(SparrowCorePlugin):
    name = "task-manager"
    celery: Celery = None
    broadcast = None

    _task_worker_enabled = False
    _task_message_queue: Redis = None
    _cli_app = typer.Typer()
    _task_commands = []
    _tasks = {}

    def __init__(self, app):
        if TASK_BROKER is not None and TASK_WORKER_ENABLED:
            self._setup_celery()
        super().__init__(app)

    def _setup_celery(self):
        environ.setdefault("CELERY_BROKER_URL", TASK_BROKER)
        environ.setdefault("CELERY_RESULT_BACKEND", TASK_BROKER)
        environ["C_FORCE_ROOT"] = "true"
        self._task_worker_enabled = True
        self.celery = Celery("tasks", broker=TASK_BROKER)
        self.celery.conf["broker_transport_options"] = {
            "max_retries": 3,
            "interval_start": 0,
            "interval_step": 0.2,
            "interval_max": 0.5,
        }

        # Enables tasks to talk to the frontend
        self._task_message_queue = Redis.from_url(TASK_BROKER)

    def register_task(self, func, *args, **kwargs):
        # Get plugin name
        name = _name_for_task(func, **kwargs)
        destructive = kwargs.get("destructive", False)
        cli_only = kwargs.get("cli_only", False)
        if destructive:
            cli_only = True

        self._cli_app.command(name=name)(func)
        task = func
        if self.celery is not None:
            task = self.celery.task(*args, **kwargs)(func)

        try:
            args_schema = create_args_schema(func)
        except RuntimeError:
            raise SparrowTaskError(
                f"Task {name} has untyped arguments, which is not allowed."
            )

        self._tasks[name] = {"func": task, "params": args_schema, "cli_only": cli_only}

        self._task_commands.append(name)
        log.debug(f"Registering task {name}")
        func._is_sparrow_task = True
        return func

    def get_task(self, name):
        task = self._tasks[name]
        if task["cli_only"]:
            raise ValueError(
                f"Task {name} is cli-only and cannot be directly requested."
            )
        return task["func"]

    def task_info(self, include_cli_tasks=False):
        """Return a list of task descriptions"""
        tasks = self._tasks
        if not include_cli_tasks:
            tasks = {k: v for k, v in self._tasks.items() if not v["cli_only"]}

        return [format_task_info(k, v) for k, v in tasks.items()]

    def on_plugins_initialized(self):
        global _tasks_to_register
        for k, v in _tasks_to_register.items():
            (func, args, kwargs) = v
            kwargs["name"] = k
            self.register_task(func, *args, **kwargs)
        _tasks_to_register = {}

    def on_setup_cli(self, cli):
        self._cli_app._add_completion = False
        typer_click_object = typer.main.get_command(self._cli_app)
        cli.add_command(typer_click_object, "tasks")

    def on_api_initialized_v2(self, api):
        self.broadcast = Broadcast(TASK_BROKER)
        api.mount("/tasks", build_tasks_api(self), name="tasks")


def format_task_info(name, _task):
    params = _task.get("params", None)
    if params is not None:
        params = params.schema()

    description = _task.get("description")
    doc = _task["func"].__doc__
    if doc is not None:
        description = doc.strip()

    return {"name": name, "description": description, "params": params}
