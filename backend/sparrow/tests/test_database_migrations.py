from os import environ
from sparrow.migrations import InstrumentSessionMigration
from sparrow.core.app import Sparrow
from macrostrat.utils import relative_path, cmd
from macrostrat.dinosaur import _create_migration, create_schema_clone
from macrostrat.database.utils import connection_args, temp_database
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
        m = _create_migration(test_app.db.engine, db.engine)

        # Check that we are not aligned
        assert not m.is_safe

        # Apply migrations
        migrations = [BasicMigration, InstrumentSessionMigration]
        for mgr in migrations:
            migration = mgr()
            migration.apply(test_app.database)

        # Migrating to the new version should now be "safe"
        m = _create_migration(test_app.database.engine, db.engine)
        assert m.is_safe

        m.apply(quiet=True)
        # Re-add changes
        m.add_all_changes()

        assert len(m.statements) == 0

    @mark.slow
    def test_migration_built_in(self, db):
        db.update_schema()

    @mark.slow
    def test_schema_clone(self, db):
        with create_schema_clone(db.engine) as engine:
            m = _create_migration(engine, db.engine)
            # Schemas should now be the same...
            assert len(m.statements) == 0
