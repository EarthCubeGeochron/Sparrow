## This should probably be refactored out into a sparrow_tasks plugin eventually

import sys
from shutil import which
from subprocess import run

import click

from ..util import CommandGroup, SparrowCommandError, exec_backend_command

shell_commands = {
    "events": "Monitor `celery` events",
    "messages": "Monitor `redis` messages",
    "celery": "Run the `celery` command-line application",
    "redis": "Run the `redis-cli` command-line application",
}


@click.group(name="tasks", cls=CommandGroup)
def tasks():
    pass


def run_local_pipeline(args):
    """Run a pipeline here, with the `sparrow-pipelines` package it was written
    against, rather than in the lab's backend."""
    exe = which("sparrow-pipeline")
    if exe is None:
        raise SparrowCommandError(
            "Running a pipeline locally needs the sparrow-pipelines package",
            details="Install it alongside the pipeline, from backend/pipelines in the Sparrow repository",
        )
    sys.exit(run([exe, "run", *args]).returncode)


@click.command(
    name="run", context_settings=dict(ignore_unknown_options=True, help_option_names=[])
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def sparrow_run(ctx, args=[]):
    """Run a task in the lab's backend, or a pipeline on this machine.

    sparrow run TASK [ARGS]...             a task, by name, in the backend
    sparrow run MODULE:PIPELINE PATHS...   a pipeline, here; a dry run unless --api is given
    """
    if len(args) > 0 and ":" in args[0]:
        return run_local_pipeline(args)
    exec_backend_command(ctx, "tasks", *args)


tasks.add_command(sparrow_run)


for k, v in shell_commands.items():
    tasks.add_shell_command(k, v, prefix="sparrow-tasks-")
