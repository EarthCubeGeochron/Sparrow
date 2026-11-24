from os import environ

from click.testing import CliRunner
from pytest import skip

from sparrow_cli import cli

runner = CliRunner()


def test_cli():
    res = runner.invoke(cli, "help")
    assert res.exit_code == 0

    for stream in (res.output, res.stdout):
        assert "--skip-hostname-check" not in stream


def test_compose():
    res = runner.invoke(cli, "compose config")
    assert res.exit_code == 0

    # We need to rework using
    # cfg = load(res.output)
    # assert cfg is not None
    # assert 'gateway' in cfg['services']


def _test_database():
    """The database the backend tests use, if it is up."""
    import socket

    url = environ.get(
        "SPARROW_TESTING_DATABASE", "postgresql://postgres@localhost:54322/sparrow_test"
    )
    try:
        socket.create_connection(("localhost", 54322), timeout=1).close()
    except OSError:
        return None
    return url


def test_access_scopes():
    from macrostrat.app_frame.environments import AccessScope

    from sparrow_cli.config.admin import access_scope

    assert access_scope(["list-users"]) == AccessScope.Read
    assert access_scope(["schema", "plan"]) == AccessScope.Read
    assert access_scope(["schema", "apply"]) == AccessScope.Schema
    assert access_scope(["schema", "migrate", "--apply"]) == AccessScope.Schema
    assert access_scope(["db-update"]) == AccessScope.Schema
    assert access_scope(["create-user"]) == AccessScope.Data
    assert access_scope(["tasks", "anything"]) == AccessScope.Data


def test_admin_command_runs_here(monkeypatch):
    """With the application installed, its commands run on this machine,
    against the database of the environment, and not in a container."""
    from sparrow_cli.config.admin import admin_available
    from sparrow_cli.util import shell

    database = _test_database()
    if not admin_available() or database is None:
        skip("Needs the application installed and the test database running")

    def no_container(*args, **kwargs):
        raise AssertionError("The command was sent to a container")

    monkeypatch.setattr(shell, "exec_or_run", no_container)
    monkeypatch.setenv("SPARROW_DATABASE", database)
    monkeypatch.setenv(
        "SPARROW_SECRET_KEY", "test_secret_must_be_at_least_32_characters"
    )
    res = runner.invoke(cli, "plugins")
    assert res.exit_code == 0
