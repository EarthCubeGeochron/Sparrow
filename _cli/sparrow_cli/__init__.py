#!/usr/bin/env python3
# The sparrow command-line application is designed to run locally on user machines,
# rather than in Docker. This gives it the ability to more easily integrate with
# the base system.

import sys
import click
from rich.console import Console
from rich import print
from sparrow.utils.logs import get_logger
from .help import echo_help
from .util.shell import (
    cmd,
    exec_or_run,
    exec_backend_command,
    find_subcommand,
    container_id,
)
from .util.command_groups import SparrowDefaultCommand
from .config import SparrowConfig
from .config.environment import is_truthy
from .config.file_loader import envbash_init_hack
from .commands import add_commands
from .meta import __version__

envbash_init_hack()

log = get_logger(__name__)

console = Console(highlight=True)


def _docker_compose(*args):
    from compose.cli.main import main

    sys.argv = ["docker-compose", *args]
    main()
    # If we're still running, escape
    sys.exit(0)


@click.group(
    name="sparrow", cls=SparrowDefaultCommand, default="main", default_if_no_args=True
)
@click.option("--verbose", is_flag=True, default=is_truthy("SPARROW_VERBOSE"))
@click.option("--offline", is_flag=True, default=is_truthy("SPARROW_OFFLINE"))
@click.pass_context
def cli(ctx, verbose=False, offline=False):
    """Startup function that sets configuration environment variables."""
    # Here is where the configuration gets set up for the entire command-line application
    ctx.obj = SparrowConfig(verbose=verbose, offline=offline)


@cli.command(
    "main",
    context_settings=dict(
        ignore_unknown_options=True,
        help_option_names=[],
        max_content_width=160,
        # Doesn't appear to have landed in Click 7? Or some other reason we can't access...
        # short_help_width=160,
    ),
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def main(ctx, args):
    rest = tuple()
    try:
        (subcommand, *rest) = args
    except ValueError:
        subcommand = "--help"

    if subcommand == "_docker-compose":
        # This is an internal, undocumented command that runs  a
        # 'bare' docker-compose, without applying Sparrow environment
        return _docker_compose(*rest)

    # Find sparrow configuration object, creating it if it doesn't exist.
    # NOTE: This is the core of the Sparrow CLI configuration system, and
    # the primary locus of setup work in the application.
    cfg = ctx.find_object(SparrowConfig)

    if subcommand in ["--help", "help"]:
        return echo_help(cli, ctx, cfg.bin_directories)

    if subcommand == "compose":
        # docker-compose respecting sparrow environment
        return _docker_compose(*rest)

    # Scan for subcommands defined as a shell command starting with `sparrow-`
    _shell_command = find_subcommand(cfg.bin_directories, subcommand)

    if _shell_command is not None:
        # Run a shell subcommand
        res = cmd(_shell_command, *rest)
        # Exit with the proper return code so shell error handling works predictably
        sys.exit(res.returncode)

    # If all else fails, try to run a subcommand in the "backend" Docker container
    return exec_backend_command(ctx, *args)


@cli.command(name="container-id")
@click.argument("container", type=str)
def _container_id(container):
    click.echo(container_id(container))


@cli.command(name="shell")
@click.argument("container", type=str, required=False, default=None)
@click.pass_context
def shell(ctx, container):
    """Get an iPython or container shell"""
    if container is not None:
        for shell in ["bash", "sh"]:
            v = exec_or_run(container, shell)
            if v.returncode == 0:
                return
        return
    print("Running [bold]iPython[/bold] shell in application context.")
    exec_backend_command(ctx, "shell")


add_commands(cli)
