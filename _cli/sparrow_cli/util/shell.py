from json import loads
from json.decoder import JSONDecodeError
from os import environ
from pathlib import Path
from subprocess import PIPE, STDOUT, CalledProcessError
from typing import List

from macrostrat.utils.logs import get_logger
from macrostrat.utils.shell import cmd as cmd_
from macrostrat.utils.shell import run as run_
from macrostrat.utils.shell import split_args
from rich import print

from .exceptions import SparrowCommandError

log = get_logger(__name__)

# Set when this installation has no Sparrow server to manage
NO_SERVER = "_SPARROW_NO_SERVER"


def find_subcommand(directories: List[Path], name: str, prefix="sparrow-"):
    if name is None:
        return None
    for dir in directories:
        fn = dir / (prefix + name)
        if fn.is_file():
            return str(fn)


def cmd(*v, **kwargs):
    kwargs["logger"] = log
    # TODO: We shouldn't print unless we specify a debug/verbose flag...
    return cmd_(*v, **kwargs)


def run(*v, **kwargs):
    kwargs["logger"] = log
    return run_(*v, **kwargs)


def compose(*args, **kwargs):
    raise_docker_engine_errors()
    return cmd("sparrow compose", *args, **kwargs)


def container_id(container):
    res = compose("ps -q", container, stdout=PIPE).stdout.strip()
    if res == "":
        return None
    return res.decode("utf-8")


def container_is_running(name):
    res = compose("exec", name, "true", stdout=PIPE, stderr=STDOUT)
    return res.returncode == 0


def exec_or_run(
    container, *args, log_level=None, run_args=("--rm",), tty=True, **popen_kwargs
):
    """Run a command against sparrow within a docker container
    This `exec`/`run` switch is added because there are apparently
    database/locking issues caused by spinning up arbitrary
    backend containers when containers are already running.
    TODO: We need a better understanding of best practices here.
    """
    compose_args = []
    if log_level is not None:
        compose_args += ["--log-level", "ERROR"]
    tty_args = []
    if not tty:
        tty_args = ["-T"]

    if container_is_running(container):
        return compose(
            *compose_args, "exec", *tty_args, container, *args, **popen_kwargs
        )
    else:
        run_args = split_args(*run_args)
        run_args = list(set([*tty_args, *run_args]))
        return compose(
            *compose_args, "run", *run_args, container, *args, **popen_kwargs
        )


def exec_backend_command(ctx, *args, **kwargs):
    """Run a command in the backend container."""
    from ..config import SparrowConfig

    cfg = ctx.find_object(SparrowConfig)
    if cfg.verbose:
        args = ["--verbose"] + list(args)

    return exec_sparrow(*args, **kwargs)


# The configuration of this invocation, for commands that have no context
_config = None


def set_config(cfg):
    global _config
    _config = cfg


def exec_sparrow(*args, **kwargs):
    """Run one of the application's administrative commands, on this machine."""
    from ..config.admin import run_admin_command

    for key in ("log_level", "run_args", "tty"):
        kwargs.pop(key, None)
    return run_admin_command(_config, split_args(*args), **kwargs)


def has_command(command):
    try:
        res = cmd(f"which {command}", check=True, stdout=PIPE)
        return res.returncode == 0
    except CalledProcessError:
        return False


def fail_without_command(command):
    if not has_command(command):
        raise SparrowCommandError(
            f"Cannot find the {command} command. Is it installed?"
        )


def fail_without_docker_command():
    fail_without_command("docker")


def fail_without_docker_running():
    try:
        from docker import from_env
    except ImportError as exc:
        raise SparrowCommandError(
            "Managing a Sparrow server needs Docker support",
            details="Install it with: pip install 'sparrow-cli\\[server]'",
        ) from exc
    try:
        from_env()
    except Exception as exc:
        raise SparrowCommandError(
            "Cannot connect to the Docker daemon. Is Docker running?", details=str(exc)
        ) from exc


def raise_docker_engine_errors():
    k = "_SPARROW_CHECKED_DOCKER_ENGINE"
    if environ.get(k) == "1":
        return
    if environ.get(NO_SERVER) == "1":
        raise SparrowCommandError(
            "This command manages a Sparrow server, and there is none here",
            details="Run it from a lab's directory, with the Sparrow application installed.",
        )
    fail_without_docker_command()
    fail_without_docker_running()
    res = cmd("docker info --format '{{json .ServerErrors}}'", stdout=PIPE)
    environ[k] = "1"
    try:
        errors = loads(str(res.stdout, "utf-8"))
    except JSONDecodeError:
        print(res.stdout)
        return
    if errors is not None and len(errors) > 0:
        raise SparrowCommandError(errors[0])
