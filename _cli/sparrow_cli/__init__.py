#!/usr/bin/env python3
# The sparrow command-line application is designed to run locally on user machines,
# rather than in Docker. This gives it the ability to more easily integrate with
# the base system.

import sys
import click
from rich.console import Console
from rich import print
from .base import cli, SparrowConfig
from .help import echo_help
from .util import cmd, compose, exec_or_run, find_subcommand, container_id
from .test import sparrow_test  # noqa
from .database import sparrow_db  # noqa
from .docs import sparrow_docs  # noqa
from .dev import sparrow_dev  # noqa
from .containers import sparrow_up, sparrow_logs
from .build import sparrow_build

console = Console(highlight=True)


@cli.command(
    "main",
    context_settings=dict(
        ignore_unknown_options=True,
        help_option_names=[],
    ),
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
        echo_help(ctx, cfg.bin_directories)
        sys.exit(0)

    if subcommand == "compose":
        return compose(*rest)

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


cli.add_command(sparrow_up, name="up")
cli.add_command(sparrow_logs, name="logs")
cli.add_command(sparrow_build, name="build")
cli.add_command(sparrow_dev, name="dev")
