import click
import sys
from os import environ, path, chdir
from rich import print
from click_default_group import DefaultGroup
from .base import cli, SparrowConfig
from .util import find_subcommand, cmd
from .help import format_description
from .group import CommandGroup

# Commands inherited from earlier shell version of CLI.
shell_commands = {
    "await": "Utility that blocks until database is ready",
    "backup": "Backup database to `SPARROW_BACKUP_DIR`",
    "drop": "Drop the `Sparrow` database. [[DANGEROUS]]",
    "export": "Export database to a binary `pg_dump` archive",
    "graph": "Graph database schema to `dot` format.",
    "import": "Import database from binary `pg_dump` archive",
    "migration": "Generate a changeset against the optimal database schema",
}


@cli.group(name="db", cls=CommandGroup)
@click.pass_context
def sparrow_db(ctx):
    pass


for k, v in shell_commands.items():
    sparrow_db.add_shell_command(k, v, prefix="sparrow-db-")
