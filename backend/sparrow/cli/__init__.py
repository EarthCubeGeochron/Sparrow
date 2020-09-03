import click
from os import path, environ, devnull
from click import echo, style, secho
from sqlalchemy import create_engine
from sys import exit
from json import dumps
from click_plugins import with_plugins
from pkg_resources import iter_entry_points
from contextlib import redirect_stdout
from subprocess import run
import logging
from .util import with_database, with_app, with_full_app
from ..util import working_directory
from ..app import App
from ..auth.create_user import create_user


def _build_app_context(config):
    app = App(__name__, config=config, verbose=False)
    app.load()
    return app


class SparrowCLI(click.Group):
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
@with_database
def init_database(db, drop=False):
    """
    Initialize database schema (non-destructive)
    """
    db.initialize(drop=drop)


@cli.command(name="create-views")
@with_database
def create_views(db):
    """
    Recreate views only (without building rest of schema)
    """
    # Don't need to build the app just for this
    with working_directory(__file__):
        db.exec_sql("../database/fixtures/05-views.sql")


@cli.command(name="serve")
@with_full_app
def dev_server(app):
    """
    Run a development WSGI server
    """
    app.run(debug=True, host="0.0.0.0")


@cli.command(name="console")
@with_full_app
def console(app):
    """
    Get a Python shell within the application
    """
    from IPython import embed

    with app.app_context():
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
    with app.app_context():
        for p in app.plugins.order_plugins():
            print(p.name)
