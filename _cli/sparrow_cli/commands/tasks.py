## This should probably be refactored out into a sparrow_tasks plugin eventually

import click
from ..util import CommandGroup, exec_or_run

shell_commands = {
    "events": "Monitor `celery` events",
    "messages": "Monitor `redis` messages",
    "celery": "Run the `celery` command-line application",
    "redis": "Run the `redis-cli` command-line application",
}


@click.group(name="tasks", cls=CommandGroup)
def tasks():
    pass


@tasks.command(name="run")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def sparrow_run(args=[]):
    exec_or_run("backend", "/app/sparrow/__main__.py", "tasks", *args)


for k, v in shell_commands.items():
    tasks.add_shell_command(k, v, prefix="sparrow-tasks-")
