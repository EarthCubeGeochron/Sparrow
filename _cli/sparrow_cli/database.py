import click
from .base import cli
from .group import CommandGroup
from .util import container_id, container_is_running, run, compose


def dump_database(dbname, out_file):
    if not container_is_running("db"):
        compose("up db")
    _id = container_id("db")
    with open(out_file, "w") as f:
        run("docker exec", _id, "pg_dump -Fc -C -Upostgres", dbname, stdout=f)


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
    "import": "Import database from binary `pg_dump` archive",
}


@cli.group(name="db", cls=CommandGroup)
@click.pass_context
def sparrow_db(ctx):
    pass


@sparrow_db.command(name="migration")
def migration():
    """Generate a changeset against the optimal database schema"""
    compose("run --rm", "-T", "backend", "sparrow db migration")


for k, v in shell_commands.items():
    sparrow_db.add_shell_command(k, v, prefix="sparrow-db-")
