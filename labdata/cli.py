import click
from click import echo, style
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sys import exit

from .util import working_directory
from .app import App, construct_app
from .database import Database

cli = click.Group()

def abort(message, status=1):
    echo(style("ABORTING: ", fg='red', bold=True)+message)
    exit(status)

def get_database(ctx, param, value):
    try:
        app = App(__name__, config=value)
        return app.database
    except ValueError:
        raise click.BadParameter('Invalid database specified')
    except OperationalError as err:
        dbname = click.style(app.dbname, fg='cyan', bold=True)
        abort(f"Database {dbname} does not exist.")

with_database = click.option('--config', 'db', type=str,
                    envvar="LABDATA_CONFIG", required=True,
                    callback=get_database)

@cli.command(name='init')
@with_database
@click.option('--drop', is_flag=True, default=False)
def init_database(db, drop=False):
    db.initialize(drop=drop)

@cli.command(name='create-views')
@with_database
def create_views(db):
    # Don't need to build the app just for this
    with working_directory(__file__):
        db.exec_sql("sql/03-create-views.sql")

@cli.command(name='serve')
@with_database
def dev_server(db):
    app = construct_app(db)
    app.run(debug=True)

@cli.command(name='shell')
@with_database
def shell(db):
    from IPython import embed
    app = construct_app(db)
    with app.app_context():
        embed()
