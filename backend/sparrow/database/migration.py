from sqlalchemy import create_engine
from contextlib import contextmanager, redirect_stdout
from sqlalchemy_utils import create_database, database_exists, drop_database
from schemainspect import get_inspector
from schemainspect.misc import quoted_identifier
from migra import Migration
from migra.statements import check_for_drop
import sys
from .util import _exec_raw_sql
from sparrow_utils import get_logger

log = get_logger(__name__)


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


@contextmanager
def _target_db(url):
    from sparrow.app import Sparrow

    with temp_database(url) as engine:
        app = Sparrow(database=url)
        app.init_database()
        yield engine


def create_migration(db, safe=True):
    url = "postgres://postgres@db:5432/sparrow_temp_migration"
    with _target_db(url) as target:
        return _create_migration(db.engine, target)


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
def create_schema_clone(
    engine, db_url="postgres://postgres@db:5432/sparrow_schema_clone"
):
    with temp_database(db_url) as clone_engine:
        clone_engine.dialect.server_version_info = engine.dialect.server_version_info
        m = _create_migration(clone_engine, engine)
        m.apply()
        yield clone_engine


def has_column(engine, table, column):
    insp = get_inspector(engine)
    tbl = insp.tables[table]
    for col in tbl.columns:
        if col.name == column:
            return True
    return False


class SparrowMigration:
    name = None

    def should_apply(self, engine, target, migrator):
        return False

    def apply(self, engine):
        pass


class SparrowDatabaseMigrator:
    target_url = "postgres://postgres@db:5432/sparrow_temp_migration"
    dry_run_url = "postgres://postgres@db:5432/sparrow_schema_clone"

    def __init__(self, db, migrations=[]):
        self.db = db
        self._migrations = migrations

    def add_migration(self, migration):
        assert issubclass(migration, SparrowMigration)
        self._migrations.append(migration)

    def add_module(self, module):
        for _, obj in module.__dict__.items():
            try:
                assert issubclass(obj, SparrowMigration)
            except (TypeError, AssertionError):
                continue
            if obj is SparrowMigration:
                continue
            self.add_migration(obj)

    def apply_migrations(self, engine):
        """This is the magic function where an ordered changeset gets
        generated and applied"""
        migrations = [m for m in self._migrations if m.should_apply(engine)]
        log.info("Applying manual migrations")
        while len(migrations) > 0:
            n = len(migrations)
            log.info(f"Found {n} migrations to apply")
            for m in migrations:
                log.info(f"Applying migration {m.name}")
                m.apply(engine)
            migrations = [m for m in migrations if m.should_apply(engine)]

    def _run_migration(self, engine, target, check=False):
        m = _create_migration(engine, target)
        if len(m.statements) == 0:
            log.info("No migration necessary")
            return

        if m.is_safe:
            log.info("Applying automatic migration")
            m.apply()
            return

        self.apply_migrations(engine)

        # Migrating to the new version should now be "safe"
        m = _create_migration(engine, target)
        assert m.is_safe

        m.apply()
        # Re-add changes
        m.add_all_changes()

        assert len(m.statements) == 0

    def dry_run_migration(self, target):
        with create_schema_clone(self.db.engine, db_url=self.dry_run_url) as src:
            self._run_migration(src, target)

    def run_migration(self, dry_run=True):
        with _target_db(self.target_url) as target:
            if dry_run:
                self.dry_run_migration(target)
            self._run_migration(self.db.engine, target)
