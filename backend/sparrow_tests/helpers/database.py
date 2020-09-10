import os
from contextlib import contextmanager
from sparrow.database.migration import temp_database


def connection_args(engine):
    uri = engine.url
    return f"-U {uri.username} -h {uri.host} -p {uri.port}"


@contextmanager
def testing_database(conn_string):
    """Create a testing database and tear it down after tests."""
    with temp_database(conn_string) as engine:
        # This makes sure we can run Sparrow by specifying the database
        # There is probably a cleaner way to do this.
        os.environ["SPARROW_DATABASE"] = conn_string
        yield engine
