from os import environ, chdir
from subprocess import run, PIPE, STDOUT
from shlex import split
from .env import validate_environment


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
