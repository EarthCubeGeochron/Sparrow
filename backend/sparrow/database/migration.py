from sqlalchemy import create_engine
from contextlib import contextmanager, redirect_stdout
from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlalchemy.exc import ProgrammingError, IntegrityError
from schemainspect import get_inspector
from schemainspect.misc import quoted_identifier
from migra import Migration
from migra.statements import check_for_drop
import sys
from .util import _exec_raw_sql, run_sql
from sparrow_utils import get_logger, cmd
from sqlalchemy import text
import os

log = get_logger(__name__)


class AutoMigration(Migration):
    def changes_omitting_view_drops(self):
        nsel_drops = self.changes.non_table_selectable_drops()
        for stmt in self.statements:
            if stmt in nsel_drops:
                continue
            yield stmt

    def _exec(self, sql, quiet=False):
        """Execute SQL unsafely on an sqlalchemy Engine"""
        if not quiet:
            return _exec_raw_sql(self.s_from, sql)
        try:
            self.s_from.execute(text(sql))
        except (ProgrammingError, IntegrityError) as err:
            log.debug(err)

    def apply(self, quiet=False):
        n = len(self.statements)
        log.debug(f"Applying migration with {n} operations")
        for stmt in self.statements:
            self._exec(stmt, quiet=quiet)
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
    if not database_exists(conn_string):
        create_database(conn_string)
    try:
        yield create_engine(conn_string)
    finally:
        drop_database(conn_string)


def _create_migration(db_engine, target, safe=True):
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

    log.debug("Creating migration target")
    with temp_database(url) as engine:
        app = Sparrow(database=url)
        with redirect_stdout(open(os.devnull, "w")):
            app.init_database()
        yield engine


def create_migration(db, safe=True):
    url = "postgresql://postgres@db:5432/sparrow_temp_migration"
    with _target_db(url) as target, redirect_stdout(sys.stderr):
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


def dump_schema(engine):
    conn_flags = f"-h {engine.url.host} -p {engine.url.port} -U {engine.url.username}"
    if password := engine.url.password:
        conn_flags += f" -P {password}"

    res = cmd(
        "pg_dump",
        "--schema-only",
        conn_flags,
        engine.url.database,
        capture_output=True,
    )
    return res.stdout


@contextmanager
def create_schema_clone(
    engine, db_url="postgresql://postgres@db:5432/sparrow_schema_clone"
):
    schema = dump_schema(engine)
    with temp_database(db_url) as clone_engine:
        # Not sure why we have to mess with this, but we do
        clone_engine.dialect.server_version_info = engine.dialect.server_version_info
        run_sql(clone_engine, schema)
        # Sometimes, we still have some differences, annoyingly
        m = _create_migration(clone_engine, engine)
        m.apply(quiet=True)
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
    target_url = "postgresql://postgres@db:5432/sparrow_temp_migration"
    dry_run_url = "postgresql://postgres@db:5432/sparrow_schema_clone"

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
        if len(migrations) == 0:
            log.info(f"Found no migrations to apply")
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
            log.info("No automatic migration necessary")
            return

        if m.is_safe:
            log.info("Applying automatic migration")
            m.apply(quiet=True)
            return

        self.apply_migrations(engine)

        # Migrating to the new version should now be "safe"
        m = _create_migration(engine, target)
        assert m.is_safe

        m.apply(quiet=True)
        # Re-add changes (this is time-consuming)
        # m.add_all_changes()
        # assert len(m.statements) == 0

    def dry_run_migration(self, target):
        log.info("Running dry-run migration")
        with create_schema_clone(self.db.engine, db_url=self.dry_run_url) as src:
            self._run_migration(src, target)
        log.info("Migration dry run successful")

    def run_migration(self, dry_run=True):
        with _target_db(self.target_url) as target:
            if dry_run:
                self.dry_run_migration(target)
            log.info("Running migration")
            self._run_migration(self.db.engine, target)
            log.info("Finished running migration")
