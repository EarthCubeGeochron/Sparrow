import click
import sys
from ..util import (
    CommandGroup,
    container_id,
    container_is_running,
    compose,
    exec_sparrow,
)
from sparrow_utils.shell import cmd
from subprocess import PIPE
from rich import print
from rich.console import Console

console = Console()


def dump_database(dbname, out_file):
    if not container_is_running("db"):
        compose("up db")
    _id = container_id("db")
    with open(out_file, "w") as f:
        cmd("docker exec", _id, "pg_dump -Fc -C -Upostgres", dbname, stdout=f)


# container_id=$(sparrow compose ps -q db 2>/dev/null)
#
# if [ -z $container_id ]; then
#   echo "Sparrow db container must be running"
#   exit 1
# fi
#
# docker exec $container_id \
#   pg_dump -Fc -C -Upostgres -f $internal_name sparrow
#
# docker cp "$container_id:$internal_name" "$1"
#
# docker exec $container_id rm -f $internal_name


# Commands inherited from earlier shell version of CLI.
shell_commands = {
    "await": "Utility that blocks until database is ready",
    "backup": "Backup database to `SPARROW_BACKUP_DIR`",
    "drop": "Drop the `Sparrow` database. [[DANGEROUS]]",
    "export": "Export database to a binary `pg_dump` archive",
    "graph": "Graph database schema to `dot` format.",
    "import": "Import database from binary `pg_dump` archive"
}


@click.group(name="db", cls=CommandGroup)
@click.pass_context
def sparrow_db(ctx):
    pass


@sparrow_db.command(
    name="migration", context_settings=dict(ignore_unknown_options=True)
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def migration(args):
    """Generate a changeset against the optimal database schema"""
    exec_sparrow("db-migration", *args)


@sparrow_db.command(name="drop-cache")
def drop_cache():
    """Drop the cache of SQLAlchemy models maintained by the backend container."""
    exec_sparrow("db-drop-cache")


@sparrow_db.command(name="update", context_settings=dict(ignore_unknown_options=True))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def update(args):
    """Update the database schema"""
    exec_sparrow("db-update", *args)


@sparrow_db.command(name="check-schema")
@click.option("--quiet", is_flag=True, default=False, help="Suppress output")
def check_database(quiet: bool = False):
    """Check that the database schema is up to date"""

    if not quiet:
        console.status("[bold green]Checking database schema...")
    res = exec_sparrow(
        "db-migration --hide-view-changes", tty=False, capture_output=True
    )
    migration_sql = res.stdout.decode("utf-8").strip("\n ")

    if migration_sql == "" or migration_sql is None:
        print("[green bold]The database schema is up to date!")
        sys.exit(0)
    else:
        print("[red bold]The Sparrow database does not match its target schema.")
        print(
            "[dim]You may need to run migrations with [cyan]sparrow db update[/cyan]."
        )
        print("[dim]" + migration_sql)
        sys.exit(1)


for k, v in shell_commands.items():
    sparrow_db.add_shell_command(k, v, prefix="sparrow-db-")
