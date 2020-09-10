import os
from sparrow.app import App
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy_utils import create_database, database_exists, drop_database
from migra import Migration


@contextmanager
def temp_database(conn_string):
    """Create a temporary database and tear it down after tests."""
    engine = create_engine(conn_string)

    if not database_exists(engine.url):
        create_database(engine.url)
    try:
        yield engine
    finally:
        drop_database(engine.url)


def db_migration(db, safe=True):
    """Create a database migration against the idealized schema"""
    url = "postgres://postgres@db:5432/sparrow_temp_migration"
    with temp_database(url) as engine:
        os.environ["SPARROW_DATABASE"] = url
        app = App(__name__)
        app.database.initialize()

        m = Migration(db.engine, engine)
        m.set_safety(safe)
        # Not sure what this does
        m.add_all_changes()
        for s in m.statements:
            print(s)
