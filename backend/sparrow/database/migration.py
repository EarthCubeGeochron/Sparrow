from sparrow.app import Sparrow
from sqlalchemy import create_engine
from contextlib import contextmanager, redirect_stdout
from sqlalchemy_utils import create_database, database_exists, drop_database
from schemainspect import get_inspector
from migra import Migration
from migra.statements import check_for_drop
import sys
from .util import _exec_raw_sql


class AutoMigration(Migration):
    def changes_omitting_view_drops(self):
        nsel_drops = self.changes.non_table_selectable_drops()
        for stmt in self.statements:
            if stmt in nsel_drops:
                continue
            yield stmt

    def apply(self):
        for stmt in self.statements:
            _exec_raw_sql(self.s_from, stmt)
        self.changes.i_from = get_inspector(
            self.s_from, schema=self.schema, exclude_schema=self.exclude_schema
        )

        safety_on = self.statements.safe
        self.clear()
        self.set_safety(safety_on)

    @property
    def is_safe(self):
        """We have a looser definition of safety than core Migra; ours involves not
        destroying data.
        Dropping 'non-table' items (such as views) is OK to do without checking with
        the user. Usually, these views are just dropped and recreated anyway when dependent
        tables change."""
        # We could try to apply 'non-table-selectable drops' first and then check again...
        unsafe = any(check_for_drop(s) for s in self.changes_omitting_view_drops())
        return not unsafe

    def print_changes(self):
        statements = "\n".join(self.statements)
        print(statements, file=sys.stderr)


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


def _create_migration(db_engine, target, safe=True):
    with redirect_stdout(sys.stderr):
        # For some reason we need to patch this...
        target.dialect.server_version_info = db_engine.dialect.server_version_info

        m = AutoMigration(db_engine, target)  # , exclude_schema="core_view")
        m.set_safety(safe)
        # Not sure what this does
        m.add_all_changes()
        return m


def create_migration(db, safe=True):
    url = "postgres://postgres@db:5432/sparrow_temp_migration"
    with temp_database(url) as engine:
        app = Sparrow(database=url)
        app.init_database()
        return _create_migration(db.engine, engine)


def needs_migration(db):
    migration = create_migration(db)
    return len(migration.statements) == 0


def db_migration(db, safe=True, apply=False):
    """Create a database migration against the idealized schema"""
    m = create_migration(db, safe=safe)
    print("===MIGRATION BELOW THIS LINE===", file=sys.stderr)
    for s in m.statements:
        if apply:
            run_sql(db.session, s)
        else:
            print(s, file=sys.stdout)


@contextmanager
def create_schema_clone(db, db_url="postgres://postgres@db:5432/sparrow_schema_clone"):
    with temp_database(db_url) as engine:
        engine.dialect.server_version_info = db.engine.dialect.server_version_info
        m = _create_migration(engine, db.engine)
        m.apply()
        yield engine


class SparrowDatabaseMigrator:
    def __init__(self, db):
        self.db = db

    def create_database_clone(self):
        """Clone the current database to create a schema-identical database"""
        pass