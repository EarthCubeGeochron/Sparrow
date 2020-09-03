from os import environ, chdir
from subprocess import run, PIPE, STDOUT
from shlex import split
from .env import validate_environment
from typing import List
from pathlib import Path


def find_subcommand(directories: List[Path], name: str, prefix="sparrow-"):
    if name is None:
        return None
    for dir in directories:
        fn = dir / (prefix + name)
        if fn.is_file():
            return str(fn)


def cmd(*v, **kwargs):
    val = " ".join(v)
    return run(split(val), **kwargs)


def compose(*args, **kwargs):

    validate_environment()

    chdir(environ["SPARROW_PATH"])
    overrides = environ.get("_SPARROW_DEPRECATED_OVERRIDES", "")
    return cmd("docker-compose", overrides, *args, **kwargs)


def container_is_running(name):
    res = compose("exec", name, "true", stdout=PIPE, stderr=STDOUT)
    return res.returncode == 0


def exec_or_run(container, *args, log_level=None, run_args=("--rm",)):
    """Run a command against sparrow within a docker container
    This `exec`/`run` switch is added because there are apparently
    database/locking issues caused by spinning up arbitrary
    backend containers when containers are already running.
    TODO: We need a better understanding of best practices here.
    """
    compose_args = []
    if log_level is not None:
        compose_args += ["--log-level", "ERROR"]
    if container_is_running("backend"):
        return compose(*compose_args, "exec", container, *args)
    else:
        return compose(*compose_args, "run", *run_args, container, *args)
