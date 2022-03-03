## This should probably be refactored out into a sparrow_tasks plugin eventually

import click
from ..util import CommandGroup, exec_backend_command

shell_commands = {
    "events": "Monitor `celery` events",
    "messages": "Monitor `redis` messages",
    "celery": "Run the `celery` command-line application",
    "redis": "Run the `redis-cli` command-line application",
}


@click.group(name="tasks", cls=CommandGroup)
def tasks():
    pass


@tasks.command(
    name="run", context_settings=dict(ignore_unknown_options=True, help_option_names=[])
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def sparrow_run(ctx, args=[]):
    exec_backend_command(ctx, "tasks", *args)


for k, v in shell_commands.items():
    tasks.add_shell_command(k, v, prefix="sparrow-tasks-")
