import os
from click import echo
from sparrow.util import run
from time import sleep
from sqlalchemy import create_engine, exc
from contextlib import contextmanager


def db_exists(engine):
    try:
        with engine.connect():
            return True
    except exc.OperationalError:
        return False
    return False


def connection_args(engine):
    uri = engine.url
    return f"-U {uri.username} -h {uri.host} -p {uri.port}"


@contextmanager
def testing_database(conn_string):
    """Create a testing database and tear it down after tests."""
    engine = create_engine(conn_string)

    dbargs = connection_args(engine)

    if not db_exists(engine):
        run("createdb", dbargs, engine.url.database)

    while not run("pg_isready", dbargs).returncode == 0:
        echo("Waiting for database...")
        sleep(1)

    # This makes sure we can run Sparrow by specifying the database
    # There is probably a cleaner way to do this.
    os.environ["SPARROW_DATABASE"] = conn_string

    try:
        yield engine
    finally:
        run("dropdb", dbargs, engine.url.database)
