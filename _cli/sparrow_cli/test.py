import click
import sys
from os import environ, path, chdir
from rich import print
from click_default_group import DefaultGroup
from .util import cmd
from .base import cli


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


__ctx = dict(ignore_unknown_options=True, help_option_names=[])


@cli.group(name="test", cls=DefaultGroup, default="app", default_if_no_args=True)
@click.pass_context
def sparrow_test(ctx):
    """Test runner for the Sparrow application. The testing framework is based on
    PyTest."""
    pth = environ.get("SPARROW_PATH", None)
    if pth is None:
        print(
            "SPARROW_PATH not found. For now, tests can only be run when "
            "a source directory is available."
        )
        ctx.exit()
    chdir(pth)


# Ideally this would be a subcommand, not its own separate command
@sparrow_test.command(
    "cli", context_settings=__ctx,
)
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cli_tests(
    ctx, pytest_args,
):
    # First, test basic operation of command-line application
    # We should probably just import pytest directly and run
    pass_conditions = {0: "Tests passed", 5: "No tests collected"}

    res = cmd("_cli/_scripts/test-cli", *pytest_args)
    if res.returncode not in pass_conditions.keys():
        print("CLI tests failed, exiting")
        sys.exit(res.returncode)
    else:
        print(f"CLI: {pass_conditions[res.returncode]}")


# Ideally this would be a subcommand, not its own separate command
@sparrow_test.command(
    "app", context_settings=__ctx,
)
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.option("--help", is_flag=True, default=False, help="Print this page and exit")
@click.option(
    "--pytest-help", is_flag=True, default=False, help="Print the PyTest help"
)
@click.option(
    "--psql",
    is_flag=True,
    default=False,
    help="Provide a psql prompt when testing concludes",
)
@click.option(
    "--teardown", is_flag=True, default=False, help="Teardown database on exit"
)
@click.pass_context
def sparrow_test(
    ctx, pytest_args, help=False, psql=False, teardown=False, pytest_help=False,
):
    """Run the Sparrow's main application tests"""
    if help:
        # We override the help method so we can add extra information.
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        print(
            "\nAll other command line options are passed to the [bold]pytest[/bold] test runner."
            "\npytest's commands can be printed using the [cyan]--pytest-help[/cyan] command."
        )
        ctx.exit()

    if pytest_help:
        cmd("pytest --help")
        ctx.exit()

    pth = environ.get("SPARROW_PATH", None)
    if pth is None:
        print(
            "SPARROW_PATH not found. For now, tests can only be run when a source directory is available."
        )
        return

    print("Running sparrow tests")

    # Main backend tests
    chdir(path.join(pth, "backend-tests"))
    compose("build --quiet")

    # Need to bring up database separately to ensure ports are mapped...
    compose("up -d db")
    # if container_is_running("backend") and not standalone:
    #     res = compose("exec backend", "/bin/run-tests", *args, flag)
    # else:
    flag = "--psql" if psql else ""
    res = compose(
        "run --rm --service-ports backend", "/bin/run-tests", *pytest_args, flag
    )
    # if "--keep-database" not in args:
    if teardown:
        compose("down")
    sys.exit(res.returncode)
