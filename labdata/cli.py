import click
from sqlalchemy import create_engine

from .util import run_sql_file, working_directory
from .app import construct_app
from .database import Database

cli = click.Group()

def validate_database(ctx, param, value):
    try:
        prefix = "postgresql://"
        if not value.startswith(prefix):
            value = f"{prefix}/{value}"
        db = Database(value)
        return db
    except ValueError:
        raise click.BadParameter('Invalid database specified')

with_database = click.option('--database', 'db', type=str,
                    envvar="LABDATA_DATABASE", required=True,
                    callback=validate_database)

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
