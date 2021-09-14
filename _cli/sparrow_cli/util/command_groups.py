import click
from click import echo, secho, style
from click_default_group import DefaultGroup
from os import environ
import sys

from ..config import SparrowConfig
from .exceptions import SparrowCommandError
from .formatting import format_description
from .shell import cmd, find_subcommand


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


class CommandGroup(click.Group):
    """A command group that allows us to specify shell subcommands to shadow"""

    def add_shell_command(self, k, v, prefix=""):
        @self.command(name=k, short_help=format_description(v))
        @click.argument("args", nargs=-1, type=click.UNPROCESSED)
        @click.pass_context
        def command(ctx, args):
            obj = ctx.find_object(SparrowConfig)
            fn = find_subcommand(obj.bin_directories, k, prefix=prefix)
            res = cmd(fn, *args)
            sys.exit(res.returncode)