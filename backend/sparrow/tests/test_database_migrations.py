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
from core_plugins.versioning import PGMementoMigration
from pytest import mark, fixture

target_db = environ.get("SPARROW_DATABASE")
testing_db = target_db + "_migration"


class BasicMigration:
    def should_apply(self, db, target):
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
            BasicMigration,
            InstrumentSessionMigration,
            SampleCheckMigration,
            DocumentTableMigration,
            PGMementoMigration,
            SampleLocationAddSRID,
        ]

        migrations = [
            m for m in migrations if m.should_apply(test_app.db.engine, db.engine, None)
        ]
        while len(migrations) > 0:
            for m in migrations:
                m.apply(test_app.db.engine)
                # We have applied this migration and should not do it again.
                migrations.remove(m)
            migrations = [
                m
                for m in migrations
                if m.should_apply(test_app.db.engine, db.engine, None)
            ]

        # Migrating to the new version should now be "safe"
        migration = _create_migration(test_app.database.engine, db.engine)
        print(list(migration.unsafe_changes()))
        assert migration.is_safe

        migration.apply(quiet=True)
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
