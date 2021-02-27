from sparrow.database.migration import create_schema_clone
from sparrow.app import Sparrow
from sparrow_utils import relative_path, cmd
from sparrow.database.migration import create_migration, _create_migration

target_db = "postgresql://postgres@db:5432/sparrow_test"
testing_db = "postgresql://postgres@db:5432/sparrow_migration_base"


class BasicMigration:
    def should_apply(self, db, target):
        # If analysis has column but target db does not
        # we should return true
        return True

    def apply(self, db):
        db.engine.execute("ALTER TABLE analysis DROP COLUMN in_plateau")


class TestDatabaseMigrations:
    def test_create_migration_base(self):
        fn = relative_path(__file__, "fixtures", "e57d74b-detrital-zircon-F-90.pg-dump")
        args = "-Upostgres -h db -p 5432"
        cmd("createdb", args, "sparrow_migration_base")
        cmd("pg_restore", args, "-d sparrow_migration_base", fn, check=True)

    def test_migration(self, db):
        test_app = Sparrow(debug=True, database=testing_db)
        test_app.setup_database()
        # We can use the existing testing database as a target
        m = _create_migration(test_app.database.engine, db.engine)

        # Check that we are not aligned
        assert not m.is_safe

        # Apply migrations
        migration = BasicMigration()
        migration.apply(test_app.database)

        # Migrating to the new version should now be "safe"
        m = _create_migration(test_app.database.engine, db.engine)
        assert m.is_safe

        m.apply()
        # Re-add changes
        m.add_all_changes()

        assert len(m.statements) == 0

    # def test_forced_migration(self, db):
    #     """Forcibly degrade the database and then
    #     see if we can get it back to normal state."""
    #     db.engine.execute("ALTER TABLE session ADD COLUMN fake_column text UNIQUE")
    #     m = create_migration(db)

    def test_schema_clone(self, db):
        with create_schema_clone(db) as engine:
            conn = engine.connect()