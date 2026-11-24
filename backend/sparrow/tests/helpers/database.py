import os
from contextlib import contextmanager

from macrostrat.database.utils import temporary_database


@contextmanager
def testing_database(conn_string, drop=True):
    """Create a testing database and tear it down after tests."""
    with temporary_database(conn_string, drop=drop, ensure_empty=True) as engine:
        # This makes sure we can run Sparrow by specifying the database
        # There is probably a cleaner way to do this.
        os.environ["SPARROW_DATABASE"] = conn_string
        yield engine
