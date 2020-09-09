import os
import sys
from click import echo
from sparrow.util import run
from time import sleep
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy_utils import create_database, database_exists, drop_database


@contextmanager
def temp_database(conn_string):
    """Create a testing database and tear it down after tests."""
    engine = create_engine(conn_string)

    if not database_exists(engine.url):
        create_database(engine.url)

    conn = engine.connect()

    try:
        yield engine
    finally:
        drop_database(engine.url)


def db_migration(db):
    url = "postgres://postgres@db:5432/sparrow_temp_migration"
    with temp_database(url) as engine:
        engine.connect()
        # m = Migration(s_current, s_target)
        # m.set_safety(False)
        # m.add_all_changes()
        #
        # if m.statements:
        #     print("THE FOLLOWING CHANGES ARE PENDING:", end="\n\n")
        #     print(m.sql)
        #     print()
        #     if input("Apply these changes?") == "yes":
        #         print("Applying...")
        #         m.apply()
        #     else:
        #         print("Not applying.")
        # else:
        #     print("Already synced.")
