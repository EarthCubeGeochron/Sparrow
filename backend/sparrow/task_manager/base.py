from celery import Task
from typer.utils import get_params_from_function
from pydantic import create_model
import sys
import traceback

from stringcase import pascalcase
from contextvars import ContextVar
from redis import Redis

from sparrow.logs import get_logger
from sparrow.context import get_plugin
from .logging import RedisQueueLogger, local_logger

log = get_logger(__name__)


class SparrowTaskError(Exception):
    ...


_tasks_to_register = {}


def create_args_schema(func):
    """Create a Pydantic representation of sparrow task parameters."""
    params = get_params_from_function(func)
    if not params:
        return None

    schema_name = pascalcase(func.__name__.strip("_")) + "Params"

    kwargs = {
        k: (v.annotation, ... if v.default is v.empty else v.default)
        for k, v in params.items()
    }
    return create_model(schema_name, **kwargs)


class SparrowTask(Task):
    _is_sparrow_task = True
    _message_queue: Redis = None
    _log_backend: RedisQueueLogger = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def log(self, text, type="info"):
        if self._log_backend is None:
            local_logger(text, type)
        self._log_backend.write_message(text, type)

    @property
    def manager(self):
        return get_plugin("task-manager")

    def __call__(self, *args, **kwargs):
        """In a celery task this function calls the run method, here you can
        set some environment variable before the run of the task"""

        self._message_queue = self.manager._task_message_queue
        channel = "sparrow:task:" + self.name
        with RedisQueueLogger(self._message_queue, channel) as self._log_backend:
            _task_context.set(self)
            self.__run_task(*args, **kwargs)

    def __run_task(self, *args, **kwargs):
        try:
            with self._log_backend.redirect_output():
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
        mgr = None
        try:
            mgr = get_plugin("task-manager")
        except (ImportError, AttributeError, ValueError):
            # Queue the task for later registration
            _tasks_to_register[task_name] = (func, args, kwargs)
        if mgr is not None:
            # Register the task right now
            mgr.register_task(func, *args, **kwargs)

        def _run_task(*args, **task_kwargs):
            """Function to run a task that is already registered to the running Sparrow application."""
            mgr = get_plugin("task-manager")
            func = mgr.get_task(task_name)
            return func(*args, **task_kwargs)

        return _run_task

    return wrapper


_task_context: ContextVar[SparrowTask] = ContextVar(
    "sparrow-task-context", default=None
)


def get_running_task() -> SparrowTask:
    return _task_context.get()
