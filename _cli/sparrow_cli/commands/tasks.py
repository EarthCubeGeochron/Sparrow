## This should probably be refactored out into a sparrow_tasks plugin eventually

import click
from ..group import CommandGroup
from ..util import container_id, container_is_running, compose, exec_sparrow
from sparrow_utils.shell import cmd


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
shell_commands = {"celery": "Run the celery task manager CLI"}


@click.group(name="tasks", cls=CommandGroup)
def sparrow_tasks():
    pass


for k, v in shell_commands.items():
    sparrow_tasks.add_shell_command(k, v, prefix="sparrow-task-")
