import click
from sqlalchemy.exc import OperationalError
from os import devnull
from click import style, echo
from contextlib import redirect_stderr
from functools import update_wrapper
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


with_app = click.make_pass_decorator(App)

def with_database(cmd):
    @click.pass_context
    def new_cmd(ctx, *args, **kwargs):
        app = ctx.find_object(App)
        return ctx.invoke(cmd, app.database, *args, **kwargs)
    return update_wrapper(new_cmd, cmd)
