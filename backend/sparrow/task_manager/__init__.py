"""
Sparrow's task manager provides a way to run long-running processes
(e.g., imports), within the context of a Sparrow application.

Tasks have

- Unique names
- Autogenerated command-line applications (if desired)
- Celery task representation
- Optional stdout redirection

"""
from celery import Task, Celery
from sparrow.logs import get_logger
from os import environ
from sparrow.plugins import SparrowCorePlugin
from sparrow.context import get_plugin
from sparrow.settings import TASK_BROKER, TASK_WORKER_ENABLED
import typer
from .task_api import build_tasks_api
from redis import Redis
import sys
import traceback
from json import dumps
from time import time
from broadcaster import Broadcast
from contextlib import contextmanager
from typer.utils import get_params_from_function
from pydantic import create_model
from asyncio import sleep

log = get_logger(__name__)


class SparrowTaskError(Exception):
    ...


_tasks_to_register = {}


def create_args_schema(func):
    """Create a Pydantic representation of sparrow task parameters."""
    params = get_params_from_function(func)

    kwargs = {
        k: (v.annotation, ... if v.default is v.empty else v.default)
        for k, v in params.items()
    }
    return create_model("TaskParamModel", **kwargs)


class SparrowTaskManager(SparrowCorePlugin):
    name = "task-manager"
    celery: Celery = None
    broadcast = None

    _task_worker_enabled = False
    _cli_app = typer.Typer()
    _task_commands = []
    _celery_tasks = {}

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

    def register_task(self, func, *args, **kwargs):
        # Get plugin name
        name = kwargs.get("name", func.__name__)
        destructive = kwargs.get("destructive", False)
        cli_only = kwargs.get("cli_only", False)
        if destructive or self.celery is None:
            cli_only = True

        self._cli_app.command(name=name)(func)
        if not cli_only:
            task = self.celery.task(*args, **kwargs)(func)
            self._celery_tasks[name] = {
                "func": task,
                "params": create_args_schema(func),
            }

        self._task_commands.append(name)
        log.debug(f"Registering task {name}")
        func._is_sparrow_task = True
        return func

    def get_task(self, name):
        return self._celery_tasks[name]["func"]

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


def create_message(**kwargs):
    return dumps(dict(time=time(), **kwargs))


class RedisFileObject(object):
    def __init__(self, connection, _key, type="stdout"):
        self.key = _key
        self.type = type
        self.connection = connection
        self._time = time()
        self._buffer = ""

    def isatty(self):
        return True

    def write(self, data):
        try:
            self._buffer += data + "\n"
        except TypeError:
            self._buffer += str(data, "utf-8") + "\n"
        if time() - self._time > 1:
            self.send_message()
        else:
            self.send_delayed()

    async def send_delayed(self):
        await sleep(2)
        if time() - self._time > 1:
            self.send_message()

    def send_message(self):
        if self._buffer == "":
            return
        self.connection.publish(
            self.key, create_message(text=self._buffer, type=self.type)
        )
        self._buffer = ""
        self._time = time()

    def flush(self):
        pass

    def close(self):
        self.send_message()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


queue = Redis.from_url(TASK_BROKER)


# class SparrowContextError(Exception):
#     pass


# class WebSocketLogger(TextIOBase):
#     def __init__(self, session, loop=None, **kwargs):
#         self.session = session
#         self.loop = kwargs.get("loop", get_running_loop())

#     def write(self, __s: str) -> int:
#         # print(__s)
#         run_coroutine_threadsafe(self.session.send_json({"text": __s}), self.loop)
#         # return super().write(__s)


# def log(*args, **kwargs):
#     importer = get_running_importer()
#     if importer is None:
#         raise SparrowContextError(
#             "Cannot use importer logger outside of a running importer"
#         )
#     importer.log(*args, **kwargs)


# _importer_context: ContextVar[typing.Any] = ContextVar(
#     "sparrow-importer-context", default=None
# )


# def get_running_importer() -> typing.Any:
#     return _importer_context.get()


@contextmanager
def redirect_output_to_redis(queue, task_name):
    _old_stdout = sys.stdout
    _old_stderr = sys.stderr
    with RedisFileObject(queue, task_name, type="stdout") as stdout, RedisFileObject(
        queue, task_name, type="stderr"
    ) as stderr:
        sys.stdout = stdout
        sys.stderr = stderr
        yield
    sys.stdout = _old_stdout
    sys.stderr = _old_stderr


class SparrowTask(Task):
    _is_sparrow_task = True

    def __call__(self, *args, **kwargs):
        """In a celery task this function calls the run method, here you can
        set some environment variable before the run of the task"""
        try:
            with redirect_output_to_redis(queue, "sparrow:task:" + self.name):
                queue.publish(
                    "sparrow:task:" + self.name,
                    create_message(text="Starting task", type="control"),
                )
                return self.run(*args, **kwargs)
        except Exception as exc:
            l1 = traceback.format_exception(*sys.exc_info())
            queue.publish(
                "sparrow:task:" + self.name,
                create_message(text="".join(l1), type="error"),
            )
            raise exc
        finally:
            queue.publish(
                "sparrow:task:" + self.name,
                create_message(text="Task finished", type="control"),
            )

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # exit point of the task whatever is the state
        pass


def sparrow_task(*args, **kwargs):
    """A decorator to define a sparrow task."""
    kwargs.setdefault("base", SparrowTask)

    def wrapper(func):
        task_name = kwargs.get("name", func.__name__)
        try:
            mgr = get_plugin("task-manager")
            mgr.register_task(func, *args, **kwargs)
        except (ImportError, AttributeError, ValueError):
            _tasks_to_register[task_name] = (func, args, kwargs)

        def _run_task(*args, **kwargs):
            """Function to run a task that is already registered to the running Sparrow application."""
            mgr = get_plugin("task-manager")
            func = mgr.get_task(task_name)
            return func(*args, **kwargs)

        return _run_task

    return wrapper
