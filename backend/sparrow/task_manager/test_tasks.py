from .. import task
from click import echo


@task(name="hello")
def hello_task(name: str):
    """Say hello!"""
    text = f"Hello, {name}"
    echo(text)
    return text


class TestSparrowTaskManager:
    def test_task_manager_exists(self, app):
        mgr = app.plugins.get("task-manager")
        assert mgr is not None
        hello_task = mgr.get_task("hello")
        assert hello_task is not None
        assert hello_task._is_sparrow_task
        assert hello_task("Sparrow") == "Hello, Sparrow"
