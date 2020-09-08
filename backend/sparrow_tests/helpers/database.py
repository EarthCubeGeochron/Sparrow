import os
from click import echo
from sparrow.util import run
from time import sleep
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy_utils import create_database, database_exists, drop_database


def connection_args(engine):
    uri = engine.url
    return f"-U {uri.username} -h {uri.host} -p {uri.port}"


@contextmanager
def testing_database(conn_string):
    """Create a testing database and tear it down after tests."""
    engine = create_engine(conn_string)

    dbargs = connection_args(engine)

    if not database_exists(engine.url):
        create_database(engine.url)

    while not run("pg_isready", dbargs).returncode == 0:
        echo("Waiting for database...")
        sleep(1)

    # This makes sure we can run Sparrow by specifying the database
    # There is probably a cleaner way to do this.
    os.environ["SPARROW_DATABASE"] = conn_string

    try:
        yield engine
    finally:
        drop_database(engine.url)
