import click
from sqlalchemy.exc import OperationalError

from ..app import App
from ..database import Database


def get_database(ctx, param, value):
    try:
        app = App(__name__, config=value)
        return Database(app)
    except ValueError:
        raise click.BadParameter('Invalid database specified')
    except OperationalError:
        dbname = click.style(app.dbname, fg='cyan', bold=True)
        cmd = style(f"createdb {app.dbname}", dim=True)
        abort(f"Database {dbname} does not exist.\n"
               "Please create it before continuing.\n"
              f"Command: `{cmd}`")


kw = dict(type=str, envvar="SPARROW_BACKEND_CONFIG", required=True)
with_config = click.option('--config', 'cfg', **kw)
with_database = click.option('--config', 'db', callback=get_database, **kw)
