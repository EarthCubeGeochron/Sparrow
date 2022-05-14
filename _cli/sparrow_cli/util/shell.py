from subprocess import PIPE, STDOUT
from typing import List
from pathlib import Path
from json import loads
from os import environ
from json.decoder import JSONDecodeError

from sparrow_utils.logs import get_logger
from sparrow_utils.shell import split_args, cmd as cmd_, run as run_
from rich import print
from .exceptions import SparrowCommandError


log = get_logger(__name__)


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

    return exec_or_run("backend", "/app/sparrow/__main__.py", *args, **kwargs)


def exec_sparrow(*args, **kwargs):
    return exec_or_run("backend", "/app/sparrow/__main__.py", *args, **kwargs)

def fail_without_docker():
    res = cmd("which docker", check=True)
    if res.returncode != 0:
        raise SparrowCommandError(
            "Cannot find the docker command. Is docker installed?"
        )


def raise_docker_engine_errors():
    fail_without_docker()
    k = "_SPARROW_CHECKED_DOCKER_ENGINE"
    if not environ.get(k) == "1":
        res = cmd("docker info --format '{{json .ServerErrors}}'", stdout=PIPE)
        environ[k] = "1"
    try:
        errors = loads(str(res.stdout, "utf-8"))
    except JSONDecodeError:
        print(res.stdout)
        return
    if errors is not None and len(errors) > 0:
        raise SparrowCommandError(errors[0])
