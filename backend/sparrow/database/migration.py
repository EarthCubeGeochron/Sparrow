from macrostrat.database import Database
from macrostrat.dinosaur import MigrationManager, SchemaMigration
from macrostrat.dinosaur import db_migration as _db_migration


class SparrowMigrationError(Exception):
    pass


class SparrowMigration(SchemaMigration):
    ...


def initialize(database: Database):
    from sparrow.core import Sparrow

    sparrow = Sparrow(database=str(database.engine.url))
    sparrow.init_database(force=True)


def db_migration(db, **kwargs):
    return _db_migration(db, initialize, **kwargs)


class SparrowDatabaseMigrator(MigrationManager):
    target_url = "postgresql://postgres@db:5432/sparrow_temp_migration"
    dry_run_url = "postgresql://postgres@db:5432/sparrow_schema_clone"

    def __init__(self, db, migrations=None):
        super().__init__(db, initialize, migrations)

    def _pre_auto_migration(self, engine, target):
        from . import Database

        db = Database(engine.url)
        db.initialize()
