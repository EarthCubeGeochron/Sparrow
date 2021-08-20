from .. import task
from click import echo
from ..users.test_user_api import admin_client
from inspect import signature
from typing import get_type_hints
from typer.utils import get_params_from_function
from pydantic import create_model


@task(name="hello")
def hello_task(name: str):
    """Say hello!"""
    text = f"Hello, {name}"
    echo(text)
    return text


def _really_real(name: str, check_real: bool = True):
    pass


@task(name="really-real")
def really_real(name: str, check_real: bool = True):
    """Say hello!"""
    if check_real:
        text = f"Hello, {name}"
    else:
        text = "You're a ghost!"
    echo(text)
    return text


class TestSparrowTaskManager:
    def test_task_manager_exists(self, app):
        mgr = app.plugins.get("task-manager")
        mgr.celery.conf.task_always_eager = True
        assert mgr is not None
        hello_task = mgr.get_task("hello")
        assert hello_task is not None
        assert hello_task._is_sparrow_task
        assert hello_task("Sparrow") == "Hello, Sparrow"

    def test_task_manager_api(self, admin_client):
        res = admin_client.get("/api/v2/tasks/")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["enabled"]
        task_names = [t["name"] for t in data["tasks"]]
        assert "hello" in task_names

    def test_schema_generation(self):
        """Test that a reasonable schema is generated for a function."""
        params = get_params_from_function(_really_real)

        def get_param(v):
            return (v.annotation, ... if v.default is v.empty else v.default)

        kwargs = {k: get_param(v) for k, v in params.items()}
        ParamModel = create_model("ParamModel", **kwargs)
        schema = ParamModel.schema_json()

        assert False
