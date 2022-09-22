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

from macrostrat.database import Database
from macrostrat.database.utils import (
    _exec_raw_sql,
    run_sql,
    temp_database,
    connection_args,
)
from macrostrat.dinosaur import MigrationManager, SchemaMigration
from macrostrat.dinosaur import db_migration as _db_migration


class SparrowMigrationError(Exception):
    pass


class SparrowMigration(SchemaMigration):
    ...


def initialize(database: Database):
    from . import Database as SparrowDatabase

    sparrow_db = SparrowDatabase(database.engine.url)
    sparrow_db.initialize()


def db_migration(db, **kwargs):
    return _db_migration(db, initialize, **kwargs)


class SparrowDatabaseMigrator(MigrationManager):
    target_url = "postgresql://postgres@db:5432/sparrow_temp_migration"
    dry_run_url = "postgresql://postgres@db:5432/sparrow_schema_clone"

    def __init__(self, db, migrations=None):
        super().__init__(db, initialize, migrations)
