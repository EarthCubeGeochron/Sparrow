import click
from os import path
from click import echo, style, secho
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sys import exit
from json import dumps
from click_plugins import with_plugins
from pkg_resources import iter_entry_points
from subprocess import run

from .util import working_directory
from .app import App, construct_app
from .database import Database
from .auth.create_user import create_user

@click.group()
def cli():
    pass

def abort(message, status=1):
    prefix = "ABORTING: "
    msg = message.replace("\n","\n"+" "*len(prefix))
    echo(style(prefix, fg='red', bold=True)+msg)
    exit(status)


def get_database(ctx, param, value):
    try:
        app = App(__name__, config=value)
        return Database(app)
    except ValueError:
        raise click.BadParameter('Invalid database specified')
    except OperationalError as err:
        dbname = click.style(app.dbname, fg='cyan', bold=True)
        cmd = style(f"createdb {app.dbname}", dim=True)
        abort(f"Database {dbname} does not exist.\n"
               "Please create it before continuing.\n"
              f"Command: `{cmd}`")

kw = dict(type=str, envvar="SPARROW_BACKEND_CONFIG", required=True)
with_config = click.option('--config', 'cfg', **kw)
with_database = click.option('--config', 'db', callback=get_database, **kw)

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

# Support arbitrary subcommand loading
# https://click.palletsprojects.com/en/7.x/commands/#custom-multi-commands
# Right now we just program in each subcommand which is ugly and non-extensible
# Ideally, we'd drag in anything we can find.
name='import-earthchem'
@cli.command(name=name)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def sparrow_earthchem_vocabulary(args):
    """
    Import EarthChem vocabularies
    """
    __dirname = path.dirname(__file__)
    cmd = path.abspath(path.join(__dirname,"..","bin","sparrow-"+name))
    run([cmd, *args])
