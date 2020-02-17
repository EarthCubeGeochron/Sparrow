import click
from sqlalchemy.exc import OperationalError
from os import devnull
from click import style, echo
from contextlib import redirect_stderr
import sys

from ..app import App, construct_app as base_construct_app
from ..database import Database

def abort(err):
    echo(err, fg='red', err=True)

def construct_app(cfg):
    with open(devnull, 'w') as f:
       with redirect_stderr(f):
           return base_construct_app(cfg)


def get_database(ctx, param, value):
    try:
        app = App(__name__, config=value)
        return Database(app)
    except ValueError:
        raise click.BadParameter('Invalid database specified')
    except OperationalError:
        dbname = click.style(app.dbname, fg='cyan', bold=True)
        cmd = style(f"createdb {app.dbname}", dim=True)
        echo(f"Database {dbname} does not exist.\n"
               "Please create it before continuing.\n"
              f"Command: `{cmd}`")
        sys.exit(0)


kw = dict(type=str, envvar="SPARROW_BACKEND_CONFIG", required=True)
with_config = click.option('--config', 'cfg', **kw)
with_database = click.option('--config', 'db', callback=get_database, **kw)
