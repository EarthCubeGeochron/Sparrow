#!/usr/bin/env python3
# The sparrow command-line application is designed to run locally on user machines,
# rather than in Docker. This gives it the ability to more easily integrate with
# the base system.

import sys
import click
from rich.console import Console
from .base import cli, SparrowConfig
from .help import echo_help
from .util import cmd, compose, exec_or_run
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
        return exec_or_run("backend", "sparrow", *args)
    else:
        return cmd(_command, *rest)
