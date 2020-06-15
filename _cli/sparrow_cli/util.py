from os import environ, chdir, path
from subprocess import run, PIPE, STDOUT
from shlex import split


def cmd(*v, **kwargs):
    val = " ".join(v)
    return run(split(val), **kwargs)


def compose(*args, **kwargs):
    base = environ['SPARROW_PATH']
    main = path.join(base, "docker-compose.yaml")
    overrides = environ.get("SPARROW_COMPOSE_OVERRIDES", "")
    chdir(base)
    return cmd("docker-compose", "-f", main, overrides, *args, **kwargs)


def container_is_running(name):
    res = compose("exec", name, "true", stdout=PIPE, stderr=STDOUT)
    return res.returncode == 0
