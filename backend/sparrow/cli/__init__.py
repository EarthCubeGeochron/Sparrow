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

from .util import with_config, with_database
from ..util import working_directory
from ..app import App, construct_app
from ..auth.create_user import create_user


# https://click.palletsprojects.com/en/7.x/commands/#custom-multi-commands
class SparrowCLI(click.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This only pulls in configuration from environment variable for now,
        # but I don't see another option to support lazily loading plugins
        app = App(__name__, config=environ.get("SPARROW_BACKEND_CONFIG"))
        app.load()
        app.run_hook("setup-cli", self)


@click.group(cls=SparrowCLI)
def cli():
    pass


def abort(message, status=1):
    prefix = "ABORTING: "
    msg = message.replace("\n","\n"+" "*len(prefix))
    echo(style(prefix, fg='red', bold=True)+msg)
    exit(status)


@cli.command(name='init')
@with_database
@click.option('--drop', is_flag=True, default=False)
def init_database(db, drop=False):
    """
    Initialize database schema (non-destructive)
    """
    db.initialize(drop=drop)

@cli.command(name='create-views')
@with_database
def create_views(db):
    """
    Recreate views only (without building rest of schema)
    """
    # Don't need to build the app just for this
    with working_directory(__file__):
        db.exec_sql("database/fixtures/05-views.sql")

@cli.command(name='serve')
@with_config
def dev_server(cfg):
    """
    Run a development WSGI server
    """
    app, db = construct_app(cfg)
    app.run(debug=True, host='0.0.0.0')

@cli.command(name='shell')
@with_config
def shell(cfg):
    """
    Get a Python shell within the application
    """
    from IPython import embed
    app, db = construct_app(cfg)
    with app.app_context():
        # `using` is related to this issue:
        # https://github.com/ipython/ipython/issues/11523
        embed(using=False)

@cli.command(name='config')
@with_config
@click.argument('key', required=False)
@click.option('--json', is_flag=True, default=False)
def config(cfg, key=None, json=False):
    """
    Print configuration of backend
    """
    app, db = construct_app(cfg, minimal=True)
    if key is not None:
        print(app.config.get(key.upper()))
        return

    if json:
        res = dict()
        for k in ("LAB_NAME","DBNAME", "DATABASE","BASE_URL"):
            val = app.config.get(k)
            v = k.lower()
            res[v] = val
        print(dumps(res))
        return

    for k,v in app.config.items():
        secho(f"{k:30}", nl=False, dim=True)
        secho(f"{v}")

@cli.command(name='create-user')
@with_database
def _create_user(db):
    """
    Create an authorized user for the web frontend
    """
    create_user(db)
