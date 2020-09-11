import click
from click import Group
from .help import format_description
from .base import SparrowConfig
from .util import cmd, find_subcommand


class CommandGroup(Group):
    """A command group that allows us to specify shell subcommands to shadow"""

    def add_shell_command(self, k, v, prefix=""):
        @self.command(name=k, short_help=format_description(v))
        @click.argument("args", nargs=-1, type=click.UNPROCESSED)
        @click.pass_context
        def command(ctx, args):
            obj = ctx.find_object(SparrowConfig)
            fn = find_subcommand(obj.bin_directories, k, prefix=prefix)
            cmd(fn, *args)
