from os import environ
from sparrow.migrations import (
    InstrumentSessionMigration,
    SampleCheckMigration,
    SampleLocationAddSRID,
    SampleAttributeCascadeMigration,
)
from sparrow.core.app import Sparrow
from macrostrat.utils import relative_path, cmd
from macrostrat.dinosaur import _create_migration, create_schema_clone
from macrostrat.database.utils import connection_args, temp_database, run_sql
from sparrow.core.open_search import DocumentTableMigration
from core_plugins.versioning import PGMementoMigration, PGMemento074Migration

from pytest import mark, fixture
from macrostrat.utils import get_logger

target_db = environ.get("SPARROW_DATABASE")
testing_db = target_db + "_migration"

log = get_logger(__name__)


class BasicMigration:
    def should_apply(self, source, target, migrator):
        # If analysis has column but target db does not
        # we should return true
        return True

    def apply(self, engine):
        run_sql(engine, "ALTER TABLE analysis DROP COLUMN in_plateau")


@fixture(scope="class")
def migration_base():
    fn = relative_path(__file__, "fixtures", "e57d74b-detrital-zircon-F-90.pg-dump")
    args, dbname = connection_args(testing_db)
    with temp_database(testing_db) as engine:
        cmd("pg_restore", args, "-d", dbname, str(fn), check=True)
        yield engine


# @mark.order(-1)
class TestDatabaseMigrations:
    @mark.skip(reason="Doesn't work right now")
    def test_migration(self, db, migration_base):
        test_app = Sparrow(debug=True, database=migration_base.url)
        test_app.setup_database(automap=False)
        log.info("Initialized test database")
        # We can use the existing testing database as a target

        source = test_app.db.engine
        dest = db.engine
        migration = _create_migration(source, dest)

        # Check that we are not aligned
        assert not migration.is_safe

        # Apply migrations
        migrations = [
            DocumentTableMigration,
            PGMementoMigration,
            PGMemento074Migration,
            InstrumentSessionMigration,
            SampleCheckMigration,
            SampleLocationAddSRID,
            BasicMigration,
            SampleAttributeCascadeMigration,
        ]

        migrations = [m() for m in migrations]
        migrations = list(filter_migrations(migrations, test_app.db.engine, db.engine))

        while len(migrations) > 0:
            errors = []
            for m in migrations:
                log.info(f"Applying migration {type(m).__name__}")
                try:
                    m.apply(source)
                    # We have applied this migration and should not do it again.
                    migrations.remove(m)
                    log.info(f"Applied migration {type(m).__name__}")
                except Exception as exc:
                    log.error(f"Failed to apply migration {type(m).__name__}")
                    log.error(exc)
                    errors.append(exc)
            if len(errors) > 0 and len(errors) == len(migrations):
                log.error("Failed to apply all migrations")
                raise errors[0]
            migrations = list(
                filter_migrations(migrations, test_app.db.engine, db.engine)
            )

        log.info("Initializing database")
        test_app.database.initialize()

        log.info("Applying automatic migration")

        # Migrating to the new version should now be "safe"
        migration = _create_migration(source, dest)
        for change in migration.unsafe_changes():
            print(change)
        assert migration.is_safe

        migration.apply(quiet=False)
        migration.clear()
        migration.add_all_changes()
        # Re-add changes
        assert len(migration.statements) == 0

    @mark.slow
    def test_migration_built_in(self, db):
        db.update_schema()

    @mark.slow
    def test_schema_clone(self, db):
        with create_schema_clone(db.engine) as engine:
            m = _create_migration(engine, db.engine)
            # Schemas should now be the same...
            assert len(m.statements) == 0


def filter_migrations(migrations, source, dest):
    for m in migrations:
        if m.should_apply(source, dest, None):
            yield m
