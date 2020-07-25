import click
import sys
from os import environ, path, chdir
from rich import print
from .util import cmd


def compose(*args, **kwargs):
    env = dict(**environ)
    env.update(
        # Set a different compose project name so we don't step on running
        # applications.
        COMPOSE_PROJECT_NAME="sparrow_test",
        COMPOSE_FILE="docker-compose.sparrow-tests.yaml",
    )

    kwargs["env"] = env
    return cmd("docker-compose", *args, **kwargs)


# Ideally this would be a subcommand, not its own separate command
def sparrow_test(*args):

    pth = environ.get("SPARROW_PATH", None)
    if pth is None:
        print(
            "SPARROW_PATH not found. For now, tests can only be run when a source directory is available."
        )
        return

    print("Running sparrow tests")

    cli_args = [a for a in args if a != "--psql"]

    # First, test basic operation of command-line application
    # We should probably just import pytest directly and run
    res = cmd(path.join(pth, "_cli/_scripts/test-cli"), *cli_args)
    if res.returncode != 0:
        print("CLI tests failed, exiting")
        sys.exit(res.returncode)

    # Main backend tests
    chdir(path.join(pth, "backend-tests"))
    compose("build --quiet")

    # Need to bring up database separately to ensure ports are mapped...
    compose("up -d db")
    res = compose("run --rm --service-ports backend", "/bin/run-tests", *args)
    compose("down")
    sys.exit(res.returncode)
