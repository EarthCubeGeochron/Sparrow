## This should probably be refactored out into a sparrow_tasks plugin eventually

import sys
from os import environ
from shutil import which
from subprocess import run

import click
from macrostrat.app_frame.environments import AccessScope

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


def _lab_api(cfg, args):
    """Arguments and variables that send records to the active environment's lab."""
    settings = cfg.environments.settings
    api = settings.get("api")
    if api is None:
        raise SparrowCommandError(
            "The active environment names no lab to load into",
            details="Set `api` (and `api_token`) for it in sparrow.toml, or pass --api.",
        )
    cfg.environments.require_access(AccessScope.Data, action="loading data")
    env = dict(environ)
    token = settings.secret("api_token")
    if token is not None:
        env["SPARROW_API_TOKEN"] = token
    return [*args, "--api", str(api)], env


def run_local_pipeline(cfg, args):
    """Run a pipeline here, with the `sparrow-pipelines` package it was written
    against, rather than in the lab's backend."""
    args = list(args)
    env = None
    if "--load" in args:
        args.remove("--load")
        args, env = _lab_api(cfg, args)
    # Prefer the command of the pipeline's own environment, with its dependencies
    exe = which("sparrow-pipeline")
    if exe is not None:
        sys.exit(run([exe, "run", *args], env=env).returncode)

    if cfg.is_frozen:
        raise SparrowCommandError(
            "The bundled Sparrow application cannot import your pipeline",
            details="Install sparrow-cli in the pipeline's own Python environment and run it from there.",
        )

    from sparrow.pipelines.cli import app

    # As `python -m` would, so a pipeline beside the data can be named
    sys.path.insert(0, "")
    if env is not None:
        environ.update(env)
    app(args=["run", *args], prog_name="sparrow")


@click.command(
    name="run", context_settings=dict(ignore_unknown_options=True, help_option_names=[])
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def sparrow_run(ctx, args=[]):
    """Run a task in the lab's backend, or a pipeline on this machine.

    sparrow run TASK [ARGS]...             a task, by name, in the backend
    sparrow run MODULE:PIPELINE PATHS...   a pipeline, here, as a dry run
    sparrow run MODULE:PIPELINE PATHS... --load
                                           ...sending records to the lab of the
                                           active environment (see `sparrow env`)
    """
    if len(args) > 0 and ":" in args[0]:
        from ..config import SparrowConfig

        return run_local_pipeline(ctx.find_object(SparrowConfig), args)
    exec_backend_command(ctx, "tasks", *args)


tasks.add_command(sparrow_run)


for k, v in shell_commands.items():
    tasks.add_shell_command(k, v, prefix="sparrow-tasks-")
