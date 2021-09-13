#!/usr/bin/env python3
# The sparrow command-line application is designed to run locally on user machines,
# rather than in Docker. This gives it the ability to more easily integrate with
# the base system.

import sys
import click
from os import environ
from rich.console import Console
from rich import print
from sparrow_utils.logs import get_logger, setup_stderr_logs
from .help import echo_help
from .util import cmd, exec_or_run, find_subcommand, container_id, SparrowDefaultCommand
from .config import SparrowConfig
from .config.file_loader import load_config
from .config.environment import is_truthy
from .commands import add_commands
from .meta import __version__

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
@click.option(
    "--verbose/--no-verbose", is_flag=True, default=is_truthy("SPARROW_VERBOSE")
)
@click.pass_context
def cli(ctx, verbose=False):
    """Startup function that sets configuration environment variables. Much of the
    structure of this is inherited from when the application was bootstrapped by a
    `zsh` script.
    """
    if verbose:
        setup_stderr_logs("sparrow_cli")
        # Set verbose environment variable for nested commands
        environ["SPARROW_VERBOSE"] = "1"

    load_config()
    # First steps towards some much more object-oriented configuration
    ctx.obj = SparrowConfig(verbose=verbose)


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

    # Here is where the sparrow environment gets configured...
    # See the SparrowConfig object for more information
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
    return exec_or_run("backend", "/app/sparrow/__main__.py", *args)


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
    exec_or_run("backend", "/app/sparrow/__main__.py shell")


add_commands(cli)
