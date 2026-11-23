from contextlib import contextmanager
from os import environ
from subprocess import PIPE

from macrostrat.database import Database
from macrostrat.database.utils import connection_args, temporary_database
from macrostrat.utils import cmd
from sqlalchemy import text
from macrostrat.dinosaur import MigrationManager, SchemaMigration
from macrostrat.dinosaur import db_migration as _db_migration
from macrostrat.dinosaur import _create_migration
from macrostrat.dinosaur import has_column as _has_column
from macrostrat.dinosaur import has_table as _has_table


def has_table(engine, table):
    # Schema inspection needs a connection, not an engine
    with engine.connect() as conn:
        return _has_table(conn, table)


def has_column(engine, table, column):
    with engine.connect() as conn:
        return _has_column(conn, table, column)


def _autocommit(engine):
    return engine.execution_options(isolation_level="AUTOCOMMIT")


def create_migration(engine, target, **kwargs):
    # Autocommit keeps the comparison from holding locks that block later DDL
    return _create_migration(_autocommit(engine), _autocommit(target), **kwargs)


_view_comments_sql = """
SELECT 'COMMENT ON COLUMN '
  || quote_ident(n.nspname) || '.' || quote_ident(c.relname) || '.' || quote_ident(a.attname)
  || ' IS ' || quote_literal(d.description)
FROM pg_description d
JOIN pg_class c ON c.oid = d.objoid AND d.classoid = 'pg_class'::regclass
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = d.objsubid
WHERE c.relkind IN ('v', 'm')
ORDER BY 1
"""


def sync_view_comments(engine, target):
    """Copy view column comments from the target schema. The schema differ
    compares these but does not migrate them, and recreating a view drops them."""
    with target.connect() as conn:
        statements = conn.execute(text(_view_comments_sql)).scalars().all()
    with engine.connect() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)
        conn.commit()


def _pg_env(engine):
    env = dict(environ)
    if engine.url.password is not None:
        env["PGPASSWORD"] = engine.url.password
    return env


@contextmanager
def create_schema_clone(
    engine, db_url="postgresql://postgres@db:5432/sparrow_schema_clone"
):
    """Create a temporary database with the same schema as an existing one,
    so that migrations can be rehearsed."""
    flags, dbname = connection_args(engine)
    dump = cmd("pg_dump --schema-only", flags, dbname, stdout=PIPE, env=_pg_env(engine))
    dump.check_returncode()
    with temporary_database(db_url) as clone:
        flags, dbname = connection_args(clone)
        cmd(
            "psql --quiet",
            flags,
            dbname,
            input=dump.stdout,
            stdout=PIPE,
            env=_pg_env(clone),
        )
        yield clone


class SparrowMigrationError(Exception):
    pass


class SparrowMigration(SchemaMigration): ...


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

    def _run_migration(self, engine, target, check=False):
        super()._run_migration(_autocommit(engine), _autocommit(target), check=check)
        sync_view_comments(engine, target)

    def dry_run_migration(self, target):
        with create_schema_clone(self.db.engine, db_url=self.dry_run_url) as src:
            self._run_migration(src, target)

    def _pre_auto_migration(self, engine, target):
        from . import Database

        db = Database(engine.url)
        db.initialize()
