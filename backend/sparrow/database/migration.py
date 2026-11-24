"""Helpers for writing and rehearsing Sparrow schema migrations."""

from contextlib import contextmanager
from os import environ
from subprocess import PIPE

from macrostrat.database import Database
from macrostrat.database.utils import connection_args, temporary_database
from macrostrat.schema_management import Migration
from macrostrat.utils import cmd
from sqlalchemy import text


class SparrowMigration(Migration):
    """A migration applied in code, rather than from SQL files beside it."""

    subsystem = "core"
    readiness_state = "ga"
    load_sql_files = False


def query_is_true(sql: str, **params):
    """A migration condition: a query that returns true."""

    def _check(db: Database) -> bool:
        return bool(db.session.execute(text(sql), params).scalar())

    return _check


def has_constraint(table: str, name: str):
    return query_is_true(
        """SELECT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conname = :name AND conrelid = to_regclass(:table)
        )""",
        table=table,
        name=name,
    )


def _pg_env(engine):
    env = dict(environ)
    if engine.url.password is not None:
        env["PGPASSWORD"] = engine.url.password
    return env


@contextmanager
def create_schema_clone(engine, db_url=None):
    """Create a temporary database with the same schema as an existing one,
    so that a schema update can be rehearsed."""
    if db_url is None:
        db_url = engine.url.set(database=engine.url.database + "_schema_clone")
    flags, dbname = connection_args(engine)
    dump = cmd("pg_dump --schema-only", flags, dbname, stdout=PIPE, env=_pg_env(engine))
    dump.check_returncode()
    with temporary_database(db_url, ensure_empty=True) as clone:
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
