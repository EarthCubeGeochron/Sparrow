from sparrow.app import Sparrow
from sqlalchemy import create_engine
from contextlib import contextmanager, redirect_stdout
from sqlalchemy_utils import create_database, database_exists, drop_database
from migra import Migration
import sys


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


def create_migration(db, safe=True):
    url = "postgres://postgres@db:5432/sparrow_temp_migration"
    with redirect_stdout(sys.stderr):
        with temp_database(url) as engine:
            app = Sparrow(database=url)
            app.init_database()

            # For some reason we need to patch this...
            engine.dialect.server_version_info = db.engine.dialect.server_version_info

            m = Migration(db.engine, engine)
            m.set_safety(safe)
            # Not sure what this does
            m.add_all_changes()
    return m


def needs_migration(db):
    migration = create_migration(db)
    return len(migration.statements) == 0


def db_migration(db, safe=True, apply=False):
    """Create a database migration against the idealized schema"""
    m = create_migration(db, safe=safe)
    print("===MIGRATION BELOW THIS LINE===", file=sys.stderr)
    for s in m.statements:
        if apply:
            print(s, file=sys.stderr)
            db.session.execute(s)
        else:
            print(s, file=sys.stdout)


class SparrowMigration:
    def should_apply(self, db):
        return False

    def apply(self, db):
        pass