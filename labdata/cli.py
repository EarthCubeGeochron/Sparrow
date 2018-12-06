import click
from sqlalchemy import create_engine

from .util import run_sql_file, working_directory
from .app import construct_app

cli = click.Group()

@cli.command(name='init')
@click.argument('dbname', type=str)
def init_database(dbname):
    # Don't need to build the app just for this
    db = Database(dbname)
    with working_directory(__file__):
        db.exec_sql("sql/setup-database.sql")
        db.exec_sql("sql/create-tables.sql")

@cli.command(name='serve')
@click.argument('dbname', type=str) # For testing
def dev_server(dbname):
    app = construct_app(f"postgresql:///{dbname}")
    app.run(debug=True)
