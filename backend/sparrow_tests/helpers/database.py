import os
from click import echo
from subprocess import run
from time import sleep
from sqlalchemy import create_engine, exc
from contextlib import contextmanager


def db_exists(engine):
    try:
        engine.connect()
        return True
    except exc.OperationalError:
        return False
    return False


def get_args(engine):
    uri = engine.url
    return f"-U {uri.username} -h {uri.host} -p {uri.port} {uri.database}"


@contextmanager
def testing_database(conn_string):
    """Create a testing database and tear it down after tests."""
    engine = create_engine(conn_string)

    dbargs = get_args(engine)

    if not db_exists(engine):
        run("createdb", dbargs)

    while not run("pg_isready", dbargs).returncode == 0:
        echo("Waiting for database...")
        sleep(1)

    os.environ["SPARROW_DATABASE"] = conn_string

    try:
        yield engine
    finally:
        run("dropdb", dbargs)
