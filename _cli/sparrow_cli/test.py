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
@click.command("sparrow-test", context_settings=dict(ignore_unknown_options=True,))
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.option("--psql", is_flag=True, default=False)
@click.pass_context
def sparrow_test(ctx, pytest_args, psql=False):

    if "--help" in pytest_args:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    pth = environ.get("SPARROW_PATH", None)
    if pth is None:
        print(
            "SPARROW_PATH not found. For now, tests can only be run when a source directory is available."
        )
        return

    print("Running sparrow tests")

    # First, test basic operation of command-line application
    # We should probably just import pytest directly and run
    pass_conditions = {0: "Tests passed", 5: "No tests collected"}

    res = cmd(path.join(pth, "_cli/_scripts/test-cli"), *pytest_args)
    if res.returncode not in pass_conditions.keys():
        print("CLI tests failed, exiting")
        sys.exit(res.returncode)
    else:
        print(f"CLI: {pass_conditions[res.returncode]}")

    # Main backend tests
    chdir(path.join(pth, "backend-tests"))
    compose("build --quiet")

    flag = "--psql" if psql else ""

    # Need to bring up database separately to ensure ports are mapped...
    compose("up -d db")
    res = compose(
        "run --rm --service-ports backend", "/bin/run-tests", *pytest_args, flag
    )
    compose("down")
    sys.exit(res.returncode)
