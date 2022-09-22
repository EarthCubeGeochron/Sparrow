from contextlib import contextmanager, redirect_stdout
from sqlalchemy.exc import ProgrammingError, IntegrityError
from schemainspect import get_inspector
from migra import Migration
from migra.statements import check_for_drop
import sys
from macrostrat.utils import get_logger, cmd
from sqlalchemy import text
import os
from rich import print

from macrostrat.database.utils import (
    _exec_raw_sql,
    run_sql,
    temp_database,
    connection_args,
)
from macrostrat.dinosaur import AutoMigration, _create_migration, create_schema_clone


log = get_logger(__name__)


@contextmanager
def _target_db(url, quiet=False, redirect=sys.stderr):
    from sparrow.core.app import Sparrow

    if quiet:
        redirect = open(os.devnull, "w")

    log.debug("Creating migration target")
    with temp_database(url) as engine:
        app = Sparrow(database=url)
        with redirect_stdout(redirect):
            app.init_database()
        yield engine


def create_migration(db, safe=True, redirect=sys.stderr):
    url = "postgresql://postgres@db:5432/sparrow_temp_migration"
    with _target_db(url, redirect=redirect) as target, redirect_stdout(redirect):
        return _create_migration(db.engine, target)


def needs_migration(db):
    migration = create_migration(db)
    return len(migration.statements) == 0


def db_migration(db, safe=True, apply=False, hide_view_changes=False):
    """Create a database migration against the idealized schema"""
    m = create_migration(db, safe=safe, redirect=sys.stderr)
    stmts = m.statements
    if hide_view_changes:
        stmts = m.changes_omitting_views()
    print("===MIGRATION BELOW THIS LINE===", file=sys.stderr)
    for s in stmts:
        if apply:
            run_sql(db.session, s)
        else:
            print(s, file=sys.stdout)


def dump_schema(engine):
    flags, dbname = connection_args(engine)
    res = cmd("pg_dump", "--schema-only", flags, dbname, capture_output=True)
    return res.stdout


def has_table(engine, table):
    insp = get_inspector(engine)
    return table in insp.tables


def has_column(engine, table, column):
    insp = get_inspector(engine)
    if table not in insp.tables:
        return False
    tbl = insp.tables[table]
    for col in tbl.columns:
        if col == column:
            return True
    return False


class SparrowMigrationError(Exception):
    pass


class SparrowMigration:
    name = None

    def should_apply(self, source, target, migrator):
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
        self._migrations.append(migration())

    def add_module(self, module):
        for _, obj in module.__dict__.items():
            try:
                assert issubclass(obj, SparrowMigration)
            except (TypeError, AssertionError):
                continue
            if obj is SparrowMigration:
                continue
            self.add_migration(obj)

    def apply_migrations(self, engine, target):
        """This is the magic function where an ordered changeset gets
        generated and applied"""
        migrations = [
            m for m in self._migrations if m.should_apply(engine, target, self)
        ]
        log.info("Applying manual migrations")
        if len(migrations) == 0:
            log.info(f"Found no migrations to apply")
        while len(migrations) > 0:
            n = len(migrations)
            log.info(f"Found {n} migrations to apply")
            for m in migrations:
                log.info(f"Applying migration {m.name}")
                m.apply(engine)
                # We have applied this migration and should not do it again.
                migrations.remove(m)
            migrations = [m for m in migrations if m.should_apply(engine, target, self)]

    def _run_migration(self, engine, target, check=False):
        m = _create_migration(engine, target)
        if len(m.statements) == 0:
            log.info("No automatic migration necessary")
            return

        if m.is_safe:
            log.info("Applying automatic migration")
            m.apply(quiet=True)
            return

        self.apply_migrations(engine, target)

        # Migrating to the new version should now be "safe"
        m = _create_migration(engine, target)
        try:
            assert m.is_safe
        except AssertionError as err:
            print("[bold red]Manual migration needed! Unsafe changes:[/bold red]")
            for s in m.unsafe_changes():
                print(s, file=sys.stderr)
            raise err

        m.apply(quiet=True)
        # Re-add changes (this is time-consuming)
        # m.add_all_changes()
        # assert len(m.statements) == 0

    def dry_run_migration(self, target):
        log.info("Running dry-run migration")
        with create_schema_clone(self.db.engine, db_url=self.dry_run_url) as src:
            self._run_migration(src, target)
        log.info("Migration dry run successful")

    def run_migration(self, dry_run=True, apply=True):
        with _target_db(self.target_url) as target:
            if dry_run:
                self.dry_run_migration(target)
            if not apply:
                return
            log.info("Running migration")
            self._run_migration(self.db.engine, target)
            log.info("Finished running migration")
