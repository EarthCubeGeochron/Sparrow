"""
Administering a lab from outside it. Commands that manage a lab's database
(its schema, users, pipelines and tasks) are a package of their own,
`sparrow-admin`, and run on this machine against the database the active
environment names (`pip install 'sparrow-cli[admin]'`). A lab's services hold
only what serves requests.
"""

import sys
from contextlib import redirect_stdout
from importlib.util import find_spec
from io import StringIO
from os import environ
from pathlib import Path
from subprocess import PIPE, CompletedProcess, run
from typing import Optional

from macrostrat.app_frame.environments import AccessScope

from ..util.exceptions import SparrowCommandError
from .environments import export_settings

# What a command may change, so that the environment can ask before it does
_schema_commands = ("init", "db-update", "remove-audit-trail")
_schema_subcommands = ("apply", "sync", "provision")
_read_commands = (
    "config",
    "list-users",
    "plugins",
    "db-migration",
    "get-cli-info",
    "--help",
)


def _use_bundled_application():
    """In the bundled application, Sparrow's own code is the source tree it
    carries, which holds the schema's SQL beside the modules that apply it."""
    backend = Path(sys._MEIPASS) / "srcroot" / "backend"
    for package in (
        backend,
        backend / "admin",
        backend / "loader",
        backend / "pipelines",
    ):
        if str(package) not in sys.path:
            sys.path.insert(0, str(package))


def admin_available() -> bool:
    """Whether Sparrow's administrative commands are installed beside this one."""
    if getattr(sys, "frozen", False):
        _use_bundled_application()
    try:
        return find_spec("sparrow.admin") is not None
    except ModuleNotFoundError:
        return False


def database_url(cfg) -> Optional[str]:
    """The database of the active environment. A lab run with Docker Compose on
    this machine publishes its database on a local port."""
    url = environ.get("SPARROW_DATABASE")
    if url is not None:
        return url
    if cfg.server_available:
        port = environ.get("SPARROW_DB_PORT", "54321")
        return f"postgresql://postgres@localhost:{port}/sparrow"
    return None


def access_scope(args) -> AccessScope:
    words = [a for a in args if not a.startswith("-")]
    if len(words) == 0 or words[0] in _read_commands:
        return AccessScope.Read
    if words[0] in _schema_commands:
        return AccessScope.Schema
    if words[0] == "schema":
        if len(words) > 1 and words[1] in _schema_subcommands:
            return AccessScope.Schema
        if "--apply" in args:
            return AccessScope.Schema
        return AccessScope.Read
    return AccessScope.Data


def admin_environment(cfg, args) -> dict:
    """The environment an admin command runs in, once it is allowed to."""
    if not admin_available():
        raise SparrowCommandError(
            "Administering a lab needs Sparrow's administrative commands",
            details="Install them with: pip install 'sparrow-cli\\[admin]'",
        )
    # Credentials are needed now, and a secret manager may ask for approval
    export_settings(cfg.environments, secrets=True)
    url = database_url(cfg)
    if url is None:
        raise SparrowCommandError(
            "The active environment names no database",
            details="Set `database` for it in sparrow.toml.",
        )
    scope = access_scope(args)
    cfg.environments.require_access(scope, action=f"`sparrow {' '.join(args)}`")
    env = dict(environ)
    env["SPARROW_DATABASE"] = url
    # Set for the lab's containers, where it has another meaning
    env.pop("SPARROW_BACKEND_CONFIG", None)
    return env


def run_admin_command(cfg, args, **kwargs) -> CompletedProcess:
    """Run one of the application's administrative commands on this machine."""
    args = list(args)
    env = admin_environment(cfg, args)
    if not getattr(sys, "frozen", False):
        return run([sys.executable, "-m", "sparrow.admin", *args], env=env, **kwargs)

    # The bundled application has no interpreter to start: run in this process
    environ.update(env)
    from sparrow.admin import cli

    captured = StringIO()
    capture = kwargs.get("stdout") == PIPE or kwargs.get("capture_output", False)
    code = 0
    with redirect_stdout(captured if capture else sys.stdout):
        try:
            cli.main(args=args, prog_name="sparrow", standalone_mode=False)
        except SystemExit as err:
            code = err.code if isinstance(err.code, int) else 1
    return CompletedProcess(args, code, stdout=captured.getvalue().encode())
