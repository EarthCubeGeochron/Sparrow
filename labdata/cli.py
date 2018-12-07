import click
from sqlalchemy import create_engine

from .util import run_sql_file, working_directory
from .app import construct_app
from .database import Database

cli = click.Group()

@cli.command(name='init')
@click.argument('dbname', type=str)
def init_database(dbname):
    # Don't need to build the app just for this
    db = Database(f"postgresql:///{dbname}")
    with working_directory(__file__):
        db.exec_sql("sql/01-setup-database.sql")
        db.exec_sql("sql/02-create-tables.sql")
        db.exec_sql("sql/03-create-views.sql")

@cli.command(name='create-views')
@click.argument('dbname', type=str)
def create_views(dbname):
    # Don't need to build the app just for this
    db = Database(f"postgresql:///{dbname}")
    with working_directory(__file__):
        db.exec_sql("sql/03-create-views.sql")

@cli.command(name='serve')
@click.argument('dbname', type=str) # For testing
def dev_server(dbname):
    app = construct_app(f"postgresql:///{dbname}")
    app.run(debug=True)
