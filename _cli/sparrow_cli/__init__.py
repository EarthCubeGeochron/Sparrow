#!/usr/bin/env python3
# The sparrow command-line application is designed to run locally on user machines,
# rather than in Docker. This gives it the ability to more easily integrate with
# the base system.

import sys
import click
from rich.console import Console
from .base import cli, SparrowConfig
from .help import echo_help
from .util import cmd, compose, container_is_running
from .test import sparrow_test


console = Console(highlight=True)


def find_subcommand(directories, name):
    if name is None:
        return None
    for dir in directories:
        fn = dir / ("sparrow-" + name)
        if fn.is_file():
            return str(fn)


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
        echo_help(*cfg.bin_directories)
        sys.exit(0)

    if subcommand == "compose":
        return compose(*rest)

    _command = find_subcommand(cfg.bin_directories, subcommand)

    if _command is None:
        # Run a command against sparrow within a docker container
        # This exec/run switch is added because there are apparently
        # database/locking issues caused by spinning up arbitrary
        # backend containers when containers are already running.
        # TODO: We need a better understanding of best practices here.
        if container_is_running("backend"):
            return compose("--log-level ERROR exec backend sparrow", *args)
        else:
            return compose("--log-level ERROR run --rm backend sparrow", *args)
    else:
        return cmd(_command, *rest)


# cli.add_command(sparrow_test)
