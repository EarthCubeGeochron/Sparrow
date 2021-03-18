import os
from contextlib import contextmanager
from sparrow.database.util import temp_database
from sqlalchemy_utils import drop_database

@contextmanager
def testing_database(conn_string, drop=True):
    """Create a testing database and tear it down after tests."""
    try:
        drop_database(conn_string)
    except Exception:
        pass
    with temp_database(conn_string, drop=drop) as engine:
        # This makes sure we can run Sparrow by specifying the database
        # There is probably a cleaner way to do this.
        os.environ["SPARROW_DATABASE"] = conn_string
        yield engine
