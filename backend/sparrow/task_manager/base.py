from celery import Task
from typer.utils import get_params_from_function
from pydantic import create_model
import sys
import traceback

from contextvars import ContextVar
from redis import Redis

from sparrow.logs import get_logger
from sparrow.context import get_plugin
from .logging import create_message, redirect_output

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


def local_logger(message: str, type: str):
    if type == "stdout":
        print(message, file=sys.stdout)
    if type == "stderr":
        print(message, file=sys.stderr)
    else:
        print(type + ": " + message)


class SparrowTask(Task):
    _is_sparrow_task = True
    _message_queue: Redis = None

    def log(self, message: str, type: str = "text", **kwargs):
        queue = self.manager._task_message_queue
        if queue is None:
            local_logger(message, type)
        else:
            queue.publish(
                "sparrow:task:" + self.name,
                create_message(text=message, type=type, **kwargs),
            )

    @property
    def manager(self):
        return get_plugin("task-manager")

    def __call__(self, *args, **kwargs):
        """In a celery task this function calls the run method, here you can
        set some environment variable before the run of the task"""

        _task_context.set(self)
        try:
            with redirect_output(self.log):
                self.log("Starting task", "control")
                return self.run(*args, **kwargs)
        except Exception as exc:
            l1 = traceback.format_exception(*sys.exc_info())
            self.log("".join(l1), "error")
            raise exc
        finally:
            self.log("Task finished", "control")

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # exit point of the task whatever is the state
        pass


def _name_for_task(func, **kwargs):
    return kwargs.get("name", func.__name__).replace("_", "-")


def task(*args, **kwargs):
    """A decorator to define a sparrow task."""
    kwargs.setdefault("base", SparrowTask)

    def wrapper(func):
        task_name = _name_for_task(func, **kwargs)
        kwargs["name"] = task_name
        try:
            # Register the task right now
            mgr = get_plugin("task-manager")
            mgr.register_task(func, *args, **kwargs)
        except (ImportError, AttributeError, ValueError):
            # Queue the task for later registration
            _tasks_to_register[task_name] = (func, args, kwargs)

        def _run_task(*args, **kwargs):
            """Function to run a task that is already registered to the running Sparrow application."""
            mgr = get_plugin("task-manager")
            func = mgr.get_task(task_name)
            return func(*args, **kwargs)

        return _run_task

    return wrapper


_task_context: ContextVar[SparrowTask] = ContextVar(
    "sparrow-task-context", default=None
)


def get_running_task() -> SparrowTask:
    return _task_context.get()
