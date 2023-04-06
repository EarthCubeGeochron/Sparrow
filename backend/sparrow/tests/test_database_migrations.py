from os import environ
from sparrow.migrations import (
    InstrumentSessionMigration,
    SampleCheckMigration,
    SampleLocationAddSRID,
)
from sparrow.core.app import Sparrow
from macrostrat.utils import relative_path, cmd
from macrostrat.dinosaur import _create_migration, create_schema_clone
from macrostrat.database.utils import connection_args, temp_database
from sparrow.core.open_search import DocumentTableMigration
from core_plugins.versioning import (
    PGMementoMigration,
    PGMemento074Migration,
)
from pytest import mark, fixture
from macrostrat.utils import get_logger

target_db = environ.get("SPARROW_DATABASE")
testing_db = target_db + "_migration"

log = get_logger(__name__)


class BasicMigration:
    def should_apply(self, db, target, migrator):
        # If analysis has column but target db does not
        # we should return true
        return True

    def apply(self, db):
        db.engine.execute("ALTER TABLE analysis DROP COLUMN in_plateau")


@fixture(scope="class")
def migration_base():
    fn = relative_path(__file__, "fixtures", "e57d74b-detrital-zircon-F-90.pg-dump")
    args, dbname = connection_args(testing_db)
    with temp_database(testing_db) as engine:
        cmd("pg_restore", args, "-d", dbname, str(fn), check=True)
        yield engine


# @mark.order(-1)
class TestDatabaseMigrations:
    # @mark.xfail(reason="There is some interference between plugins right now")
    def test_migration(self, db, migration_base):

        test_app = Sparrow(debug=True, database=migration_base.url)
        test_app.setup_database(automap=False)
        # We can use the existing testing database as a target
        migration = _create_migration(test_app.db.engine, db.engine)

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
        ]

        migrations = [m() for m in migrations]

        migrations = [
            m for m in migrations if m.should_apply(test_app.db.engine, db.engine, None)
        ]
        while len(migrations) > 0:
            errors = []
            for m in migrations:
                log.info(f"Applying migration {type(m).__name__}")
                try:
                    m.apply(test_app.db.engine)
                    # We have applied this migration and should not do it again.
                    migrations.remove(m)
                    log.info(f"Applied migration {type(m).__name__}")
                except Exception as exc:
                    log.error(f"Failed to apply migration {type(m).__name__}")
                    errors.append(exc)
            if len(errors) > 0 and len(errors) == len(migrations):
                log.error("Failed to apply all migrations")
                raise errors[0]
            migrations = [
                m
                for m in migrations
                if m.should_apply(test_app.db.engine, db.engine, None)
            ]

        # Migrating to the new version should now be "safe"
        migration = _create_migration(test_app.database.engine, db.engine)
        for change in migration.unsafe_changes():
            print(change)
        assert migration.is_safe

        migration.apply(quiet=False)
        # Re-add changes
        migration.add_all_changes()
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
