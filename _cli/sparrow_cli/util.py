from subprocess import run, PIPE, STDOUT
from shlex import split
from typing import List
from pathlib import Path
from json import loads
from .exc import SparrowCommandError
from json.decoder import JSONDecodeError
from sparrow_utils.logs import get_logger
from sparrow_utils.shell import cmd as cmd_
from rich import print

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


def compose(*args, **kwargs):
    return cmd("sparrow compose", *args, **kwargs)


def container_id(container):
    res = compose("ps -q", container, stdout=PIPE).stdout.strip()
    if res == "":
        return None
    return res.decode("utf-8")


def container_is_running(name):
    res = compose("exec", name, "true", stdout=PIPE, stderr=STDOUT)
    return res.returncode == 0


def exec_or_run(container, *args, log_level=None, run_args=("--rm",), tty=True, **popen_kwargs):
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
        return compose(*compose_args, "exec", *tty_args, container, *args, **popen_kwargs)
    else:
        return compose(*compose_args, "run", *tty_args, *run_args, container, *args, **popen_kwargs)


def exec_sparrow(*args, **kwargs):
    return exec_or_run("backend", "/app/sparrow/__main__.py", *args, **kwargs)


def fail_without_docker():
    try:
        res = cmd("docker info --format '{{json .ServerErrors}}'", stdout=PIPE)
    except FileNotFoundError:
        raise SparrowCommandError("Cannot find the docker command. Is docker installed?")
    try:
        errors = loads(str(res.stdout, "utf-8"))
    except JSONDecodeError:
        print(res.stdout)
        return
    if errors is not None and len(errors) > 0:
        raise SparrowCommandError(errors[0])
