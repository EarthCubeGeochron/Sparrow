## This should probably be refactored out into a sparrow_tasks plugin eventually

import click
from ..util import CommandGroup, container_id, container_is_running, compose
from sparrow_utils.shell import cmd


# Commands inherited from earlier shell version of CLI.
shell_commands = {"celery": "Run the celery task manager CLI"}


@click.group(name="tasks", cls=CommandGroup)
def sparrow_tasks():
    pass


for k, v in shell_commands.items():
    sparrow_tasks.add_shell_command(k, v, prefix="sparrow-task-")
