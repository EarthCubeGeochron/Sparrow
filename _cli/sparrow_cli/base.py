import sys
import click
from click import echo, secho, style, Group
from click_default_group import DefaultGroup
from sparrow_utils.logs import setup_stderr_logs
from os import environ, getcwd, chdir, getenv
from pathlib import Path
from typing import Optional
from rich.console import Console
from .config.file_loader import load_config
from .exc import SparrowCommandError
from .config import SparrowConfig
from .config.environment import is_truthy


class SparrowDefaultCommand(DefaultGroup):
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except SparrowCommandError as exc:
            prefix = str(type(exc).__name__) + "\n"
            echo(
                style(prefix, bold=True, fg="red") + style(str(exc), fg="red"), err=True
            )
            details = getattr(exc, "details", "Exiting Sparrow due to an error")
            if details is not None:
                secho(details, dim=True)
            secho(
                "To see more details, re-run this command using "
                + style("sparrow --verbose", fg="cyan", dim=True),
                dim=True,
            )
            # Maybe we should reraise only if debug is set?
            if environ.get("SPARROW_VERBOSE") is not None:
                raise exc

    def parse_args(self, ctx, args):
        # Handle the edge case where we
        # pass only the '--verbose' argument
        _args = set(args)
        _args.discard("--verbose")
        if len(_args) == 0:
            args.append(self.default_cmd_name)
        super().parse_args(ctx, args)


console = Console(highlight=True)


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
