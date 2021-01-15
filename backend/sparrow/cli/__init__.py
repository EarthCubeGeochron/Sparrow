import click
from click import echo, style, secho
from sys import exit
from os import environ
from json import dumps
from click import pass_context
from .util import with_database, with_app, with_full_app
from ..util import working_directory
from ..context import get_sparrow_app
from ..auth.create_user import create_user
from ..database.migration import db_migration


def _build_app_context(config):
    return get_sparrow_app()


class SparrowCLI(click.Group):
    """Sparrow's internal command-line application is integrated tightly with
    the version that also organizes Docker containers"""

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
        obj.run_hook("setup-cli", self)


@click.group(cls=SparrowCLI)
# Get configuration from environment variable or passed
# using the `--config` flag
@click.option("--config", "cfg", type=str, required=False)
@click.pass_context
def cli(ctx, cfg=None):
    # This signature might run things twice...
    if cfg is not None:
        ctx.obj = _build_app_context(config)


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
        db.exec_sql("../database/fixtures/05-views.sql")


@cli.command(name="shell")
@with_full_app
def shell(app):
    """
    Get a Python shell within the application
    """
    from IPython import embed

    db = app.database
    # `using` is related to this issue:
    # https://github.com/ipython/ipython/issues/11523
    embed(using=False)


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
@click.option("--safe", is_flag=True, default=True)
@click.option("--apply", is_flag=True, default=False)
def _db_migration(db, safe=True, apply=False):
    db_migration(db, safe=safe, apply=apply)


def command_info(ctx, cli):
    for name in cli.list_commands(ctx):
        cmd = cli.get_command(ctx, name)
        if cmd.hidden:
            continue
        help = cmd.get_short_help_str()
        yield name, help


@cli.command(name="get-cli-info", hidden=True)
@pass_context
def _get_cli_info(ctx):
    print(dumps({k: v for k, v in command_info(ctx, cli)}))
