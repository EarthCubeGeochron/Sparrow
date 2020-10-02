#!/usr/bin/env python3
# The sparrow command-line application is designed to run locally on user machines,
# rather than in Docker. This gives it the ability to more easily integrate with
# the base system.

import sys
import click
from rich.console import Console
from rich import print
from subprocess import Popen
from .base import cli, SparrowConfig
from .help import echo_help
from .util import cmd, compose, exec_or_run, find_subcommand, container_id
from .test import sparrow_test  # noqa
from .database import sparrow_db  # noqa
from .docs import sparrow_docs  # noqa
from .env import validate_environment

console = Console(highlight=True)


@cli.command(
    "main", context_settings=dict(ignore_unknown_options=True, help_option_names=[],)
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def main(ctx, args):
    cfg = ctx.find_object(SparrowConfig)
    rest = []
    try:
        (subcommand, *rest) = args
    except ValueError:
        subcommand = "--help"

    if subcommand in ["--help", "help"]:
        echo_help(cfg.bin_directories)
        sys.exit(0)

    if subcommand == "compose":
        return compose(*rest)

    if subcommand == "up":
        # Validate the presence of SPARROW_SECREY_KEY only if we are bringing
        # the application up. Eventually, this should be wrapped into a Python
        # version of the `sparrow up` command.
        validate_environment()

    _command = find_subcommand(cfg.bin_directories, subcommand)

    if _command is None:
        return exec_or_run("backend", "sparrow", *args)
    else:
        return cmd(_command, *rest)


@cli.command(name="container-id")
@click.argument("container", type=str)
def _container_id(container):
    click.echo(container_id(container))


@cli.command(name="shell")
@click.argument("container", type=str, required=False, default=None)
def shell(container):
    """Get an iPython or container shell"""
    if container is not None:
        return exec_or_run(container, "sh")
    print("Running [bold]iPython[/bold] shell in application context.")
    exec_or_run("backend", "sparrow shell")


@cli.command(name="up")
@click.argument("container", type=str, required=False, default=None)
@click.option("--force-recreate", is_flag=True, default=False)
def sparrow_up(container, force_recreate=False):
    """Bring up the application"""
    if container is None:
        container = ""
    res = compose(
        "up --build --no-start", "--force-recreate" if force_recreate else "", container
    )
    if res.returncode != 0:
        print("[red]One or more containers did not build successfully, aborting.[/red]")
        sys.exit(res.returncode)
    p = Popen(["sparrow", "compose", "logs", "-f", "--tail=0", container])
    compose("start", container)
    p.wait()
