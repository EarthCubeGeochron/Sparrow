from click import echo
from json import loads
from pytest import fixture, raises
from sparrow.users.test_user_api import admin_client
from .task import task, create_args_schema


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

    def test_task_manager_api_enabled(self, app, tasks_api_response):
        mgr = app.plugins.get("task-manager")
        assert tasks_api_response["enabled"] == mgr._task_worker_enabled

    def test_schema_generation(self):
        """Test that a reasonable schema is generated for a function."""
        TaskParamModel = create_args_schema(_really_real)
        schema = TaskParamModel.schema_json()
        data = loads(schema)
        assert data["properties"]["check_real"]["type"] == "boolean"
