import click
from sqlalchemy.exc import OperationalError
from os import devnull
from click import style, echo
from contextlib import redirect_stderr
from functools import update_wrapper
import sys

from ..app import Sparrow


def abort(err):
    echo(err, fg="red", err=True)


def get_database(ctx, param, value):
    try:
        app = Sparrow(config=value)
        return app.database
    except ValueError:
        raise click.BadParameter("Invalid database specified")
    except OperationalError:
        dbname = click.style(app.dbname, fg="cyan", bold=True)
        cmd = style(f"createdb {app.dbname}", dim=True)
        echo(
            f"Database {dbname} does not exist.\n"
            "Please create it before continuing.\n"
            f"Command: `{cmd}`"
        )
        sys.exit(0)


with_app = click.make_pass_decorator(Sparrow)


def with_database(cmd):
    @click.pass_context
    def new_cmd(ctx, *args, **kwargs):
        app = ctx.find_object(Sparrow)
        # This seems like it should find the application context
        # correctly, but we seem to be invoking it in a different
        # context during testing...
        if app is None:
            app = Sparrow()
        return ctx.invoke(cmd, app.database, *args, **kwargs)

    return update_wrapper(new_cmd, cmd)


def with_full_app(cmd):
    """This decorator gives us an instance of the application that has been
    fully constructed (including API and database mapping). Ideally, this should
    be refactored so that construction can occur from within methods (i.e. from
    within the App object).
    """

    @click.pass_context
    def new_cmd(ctx, *args, **kwargs):
        # We should ideally be able to pass a configuration from context...
        app = ctx.find_object(Sparrow)
        # By recreating the app, we actually run constructors (wastefully)
        # twice on startup. We need to refactor the sparrow.app.construct_app
        # to mitigate this.
        app.setup_server()
        return ctx.invoke(cmd, app, *args, **kwargs)

    return update_wrapper(new_cmd, cmd)
