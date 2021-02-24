from sparrow.app import Sparrow
from sparrow_utils import relative_path, cmd
from sparrow.database.migration import _create_migration

target_db = "postgresql://postgres@db:5432/sparrow_test"
testing_db = "postgresql://postgres@db:5432/sparrow_migration_base"


class TestDatabaseMigrations:
    def test_create_migration_base(self):
        fn = relative_path(__file__, "fixtures", "e57d74b-detrital-zircon-F-90.pg-dump")
        args = "-Upostgres -h db -p 5432"
        cmd("createdb", args, "sparrow_migration_base", check=True)
        cmd("pg_restore", args, "-d sparrow_migration_base", fn, check=True)

    def test_migration(self, db):
        test_app = Sparrow(debug=True, database=testing_db)
        test_app.setup_database()
        m = _create_migration(test_app.database.engine, db.engine)
        assert len(m.statements) == 0