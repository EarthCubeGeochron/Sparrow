import click
from .base import cli, SparrowConfig
from .util import find_subcommand, cmd
from .help import format_description

# Commands inherited from earlier shell version of CLI.
shell_commands = {
    "build": "[Production]: Build the documentation static site",
    "run": "[Production]: Run the documentation site",
    "up": "Bring up a testing documentation website",
    "test": "Confirm that the documentation website is live",
}


@cli.group(name="docs")
def sparrow_docs(ctx):
    pass


for k, v in shell_commands.items():

    @sparrow_docs.command(name=k, short_help=format_description(v))
    @click.argument("args", nargs=-1, type=click.UNPROCESSED)
    @click.pass_context
    def cmd(ctx, args):
        obj = ctx.find_object(SparrowConfig)
        fn = find_subcommand(obj.bin_directories, k, prefix="sparrow-docs-")
        cmd(fn, *args)
