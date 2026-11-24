import sys
from contextlib import redirect_stdout
from json import dumps
from logging import INFO
from os import environ
from sys import exit
from typing import Optional

import click
from click import echo, pass_context, secho, style
from macrostrat.utils.logs import setup_stderr_logs

import sparrow

from ..context import get_sparrow_app
from ..plugins import SparrowPlugin
from ..util import working_directory
from .user import create_user, list_users, reset_password
from .util import add_typer_command, with_app, with_database, with_full_app


def _build_app_context(config):
    return get_sparrow_app()


class SparrowCLI(click.Group):
    """Sparrow's internal command-line application is integrated tightly with
    the version that also organizes Docker containers"""

    __plugin_context: Optional[SparrowPlugin] = None

    def __init__(self, *args, **kwargs):
        # https://click.palletsprojects.com/en/7.x/commands/#custom-multi-commands
        # https://click.palletsprojects.com/en/7.x/complex/#interleaved-commands

        # This pulls in configuration from environment variable or a configuration
        # object, if provided; I don't see another option to support lazily loading plugins
        config = kwargs.pop("config", environ.get("SPARROW_BACKEND_CONFIG"))
        # logging.disable(level=logging.WARNING)

        kwargs.setdefault("context_settings", {})
        # Ideally we would add the Application _and_ config objects to settings
        # here...
        obj = _build_app_context(config)
        kwargs["context_settings"]["obj"] = obj
        super().__init__(*args, **kwargs)
        self.run_cli_init_hook(obj)

    def run_cli_init_hook(self, app):
        """We extend the setup CLI hook-runner function to
        report back the plugin context"""
        for plugin, method in app.plugins._iter_hooks("setup-cli"):
            self.__plugin_context = plugin
            method(self)
        self.__plugin_context = None

    def add_command(self, cmd, name=None):
        if self.__plugin_context is not None:
            cmd._plugin = self.__plugin_context.name
        super().add_command(cmd, name=name)


@click.group(cls=SparrowCLI)
# Get configuration from environment variable or passed
# using the `--config` flag
@click.option("--config", "cfg", type=str, required=False)
@click.option("--verbose", "verbose", is_flag=True, required=False, default=False)
@click.pass_context
def cli(ctx, cfg=None, verbose=False):
    # This signature might run things twice...
    if cfg is not None:
        ctx.obj = _build_app_context(config)
    if verbose:
        setup_stderr_logs()


def abort(message, status=1):
    prefix = "ABORTING: "
    msg = message.replace("\n", "\n" + " " * len(prefix))
    echo(style(prefix, fg="red", bold=True) + msg)
    exit(status)


@cli.command(name="init")
@click.option("--drop", is_flag=True, default=False)
@with_app
def init_database(app, drop=False):
    """
    Initialize database schema (non-destructive)
    """
    app.init_database(drop=drop, force=True)


@cli.command(name="create-views")
@with_database
def create_views(db):
    """
    Recreate views only (without building rest of schema)
    """
    # Don't need to build the app just for this
    with working_directory(__file__):
        db.run_sql("../database/fixtures/05-views.sql")
        db.run_sql("../database/fixtures/07-apiv2views.sql")


@cli.command(name="config")
@click.argument("key", required=False)
@click.option("--json", is_flag=True, default=False)
@with_app
def config(app, key=None, json=False):
    """
    Print configuration of backend
    """
    if key is not None:
        print(app.config.get(key.upper()))
        return

    if json:
        res = dict()
        for k in ("LAB_NAME", "DBNAME", "DATABASE", "BASE_URL"):
            val = app.config.get(k)
            v = k.lower()
            res[v] = val
        print(dumps(res))
        return

    for k, v in app.config.items():
        secho(f"{k:30}", nl=False, dim=True)
        secho(f"{v}")


@cli.command(name="create-user")
@with_database
def _create_user(db):
    """
    Create an authorized user for the web frontend
    """
    create_user(db)


@cli.command(name="list-users")
@with_database
def _list_users(db):
    list_users(db)


@cli.command(name="reset-password")
@click.argument("username")
@with_database
def _reset_password(db, username):
    """
    Reset the password for an existing user
    """
    reset_password(db, username)


@cli.command(name="plugins")
@with_app
def plugins(app):
    """
    Print a list of enabled plugins
    """
    for p in app.plugins.order_plugins():
        print(p.name)


@cli.command(name="db-migration")
@with_database
def _db_migration(db):
    """Print the changes that would bring the database schema up to date."""
    # Building the schema to compare against is chatty; only the plan is output
    with redirect_stdout(sys.stderr):
        statements = db.schema_app().plan()
    for statement in statements:
        print(statement)


@cli.command(name="db-update")
@with_database
@click.option("--dry-run", is_flag=True, default=False)
def db_update(db, dry_run=False):
    setup_stderr_logs("sparrow", "macrostrat.schema_management", level=INFO)
    db.update_schema(dry_run=True, apply=not dry_run)


def _schema_app():
    from sparrow.core import get_database

    return get_database().schema_app()


def _add_schema_commands():
    """Schema management commands, shared with Macrostrat's other applications"""
    from macrostrat.schema_management.cli import create_schema_cli

    schema_cli = create_schema_cli(_schema_app)
    schema_cli._add_completion = False
    add_typer_command(cli, schema_cli, "schema", help="Manage the database schema")


_add_schema_commands()


def command_info(ctx, cli):
    for name in cli.list_commands(ctx):
        cmd = cli.get_command(ctx, name)
        if cmd.hidden:
            continue
        yield (
            name,
            {
                "help": cmd.get_short_help_str(limit=120),
                "plugin": getattr(cmd, "_plugin", None),
            },
        )


@cli.command(name="get-cli-info", hidden=True)
@pass_context
def _get_cli_info(ctx):
    print(dumps({k: v for k, v in command_info(ctx, cli)}, indent=2))


@cli.command(name="get-cli-info-v2", hidden=True)
@pass_context
def _get_cli_info_v2(ctx):
    """A new signature for get-cli-info"""
    task_mgr = sparrow.get_plugin("task-manager")
    tasks = task_mgr.task_info()

    info = {"cli_commands": {k: v for k, v in command_info(ctx, cli)}, "tasks": tasks}

    print(dumps(info, indent=2))
