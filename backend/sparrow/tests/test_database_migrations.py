from os import environ
from sparrow.core.app import Sparrow
from sparrow.database import Database
from sparrow.database.migration import create_schema_clone
from macrostrat.utils import relative_path, cmd
from macrostrat.database.utils import connection_args, temporary_database
from macrostrat.schema_management.plan import is_unsafe_statement, plan_changes

from pytest import mark, fixture
from macrostrat.utils import get_logger

target_db = environ.get("SPARROW_DATABASE")
testing_db = target_db + "_migration"

log = get_logger(__name__)


@fixture(scope="class")
def migration_base():
    fn = relative_path(__file__, "fixtures", "e57d74b-detrital-zircon-F-90.pg-dump")
    args, dbname = connection_args(testing_db)
    with temporary_database(testing_db, ensure_empty=True) as engine:
        cmd("pg_restore", args, "-d", dbname, str(fn), check=True)
        yield engine


class TestDatabaseMigrations:
    # Schema changes take locks that an open test transaction would hold
    use_isolation = False

    def test_migration(self, db, migration_base):
        test_app = Sparrow(debug=True, database=migration_base.url)
        test_app.setup_database(automap=False)
        test_db = test_app.db

        schema_app = test_db.schema_app()

        # Check that we are not aligned: the old schema cannot be updated safely
        statements = schema_app.plan()
        assert any(is_unsafe_statement(s) for s in statements)

        # Apply migrations, then the automatic update, which should now be "safe"
        log.info("Updating schema")
        test_db.update_schema(dry_run=False)

        # The schema is now the same as one built from scratch
        remaining = schema_app.plan()
        for change in remaining:
            print(change)
        assert len(remaining) == 0

        # ...and matches the testing database
        assert len(plan_changes(test_db, db)) == 0

    @mark.slow
    def test_migration_built_in(self, db):
        db.update_schema()

    @mark.slow
    def test_schema_clone(self, db):
        with create_schema_clone(db.engine) as engine:
            clone = Database(engine.url)
            # Schemas should now be the same...
            assert len(plan_changes(clone, db)) == 0
            clone.cleanup()
