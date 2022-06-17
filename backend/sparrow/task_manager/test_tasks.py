from re import I
from click import echo
from json import loads
from pytest import fixture, raises, mark
from sparrow.auth.test_auth import admin_client
from starlette.websockets import WebSocketDisconnect
from .base import SparrowTaskError, task, create_args_schema


@task(name="hello")
def hello_task(name: str):
    """Say hello!"""
    text = f"Hello, {name}"
    echo(text)
    return text


def _really_real(name: str, check_real: bool = True):
    """Say hello!"""
    if check_real:
        text = f"Hello, {name}"
    else:
        text = "You're a ghost!"
    echo(text)
    return text


task(name="kinda-real")(_really_real)


@task(name="no-args")
def a_task_with_no_args():
    return None


@task(name="sludge", cli_only=True)
def dismal_decay():
    """An underworldly task."""
    pass


@fixture
def tasks_api_response(admin_client):
    res = admin_client.get("/api/v2/tasks/")
    assert res.status_code == 200
    return res.json()["data"]


class TestSparrowTaskManager:
    def test_task_manager_exists(self, app):
        mgr = app.plugins.get("task-manager")
        assert mgr is not None
        hello_task = mgr.get_task("hello")
        assert hello_task is not None
        assert hello_task._is_sparrow_task
        assert hello_task("Sparrow") == "Hello, Sparrow"

    def test_task_manager_api(self, tasks_api_response):
        task_names = [t["name"] for t in tasks_api_response["tasks"]]
        assert "hello" in task_names
        assert "_really_real" not in task_names
        assert "kinda-real" in task_names

    def test_cli_only_tasks(self, app, tasks_api_response):
        mgr = app.plugins.get("task-manager")
        with raises(ValueError):
            mgr.get_task("sludge")
        assert mgr._tasks["sludge"]["cli_only"]
        assert "sludge" not in tasks_api_response["tasks"]

    def test_task_api_params(self, tasks_api_response):
        """Make sure that task API parameters are available on the frontend."""
        schema = unwrap_api_schema(tasks_api_response, "hello")
        assert schema["properties"]["name"] == {"title": "Name", "type": "string"}

    def test_task_api_defaults(self, tasks_api_response):
        schema = unwrap_api_schema(tasks_api_response, "kinda-real")
        cr = schema["properties"]["check_real"]
        assert cr["type"] == "boolean"
        assert cr["default"] == True

    def test_task_api_no_args(self, tasks_api_response):
        schema = unwrap_api_schema(tasks_api_response, "no-args")
        assert schema is None

    def test_task_manager_api_enabled(self, app, tasks_api_response):
        mgr = app.plugins.get("task-manager")
        assert tasks_api_response["enabled"] == mgr._task_worker_enabled

    def test_schema_generation(self):
        """Test that a reasonable schema is generated for a function."""
        TaskParamModel = create_args_schema(_really_real)
        schema = TaskParamModel.schema()
        assert schema["type"] == "object"
        assert schema["title"] == "ReallyRealParams"
        assert schema["properties"]["check_real"]["type"] == "boolean"

    def test_websocket_task_unauthorized(self, client):
        with raises(WebSocketDisconnect) as err:
            with client.websocket_connect("/api/v2/tasks/hello") as websocket:
                websocket.receive_json()
            assert err.code == 1008

    @mark.skip(reason="Websockets only work when a broker is defined")
    def test_websocket_task_running(self, app, admin_client):
        plugin = app.plugins.get("task-manager")
        with admin_client.websocket_connect("/api/v2/tasks/hello") as websocket:
            data = websocket.receive_json()
            assert data["info"] == "Bienvenue sur le websocket!"
            websocket.send_json({"action": "start", "params": {"name": "Sparrow"}})
            if plugin.broadcast is None:
                return

    def test_create_untyped_task(self):
        with raises(SparrowTaskError) as exc_info:

            @task()
            def terrible_task(bad_arg="Bleh"):
                print(bad_arg)

        assert "Task terrible-task has untyped arguments" in str(exc_info.value)


def unwrap_api_schema(tasks_api_response, name):
    """Unwrap a schema to make it easier to work with."""
    for item in tasks_api_response["tasks"]:
        if item["name"] == name:
            return item["params"]
    raise ValueError(f"No task named {name}")
