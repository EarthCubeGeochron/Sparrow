from contextlib import contextmanager
from contextvars import ContextVar

from sqlalchemy.exc import CompileError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert
from sqlalchemy.dialects import postgresql

_import_mode = ContextVar("import-mode", default="restrict")

# https://stackoverflow.com/questions/33307250/postgresql-on-conflict-in-sqlalchemy/62305344#62305344
@contextmanager
def on_conflict(action="restrict"):
    token = _import_mode.set(action)
    try:
        yield
    finally:
        _import_mode.reset(token)


@compiles(Insert, "postgresql")
def prefix_inserts(insert, compiler, **kw):
    """Conditionally adapt insert statements to use on-conflict resolution (a PostgreSQL feature)"""
    action = _import_mode.get()
    if action == "do-update":
        try:
            params = insert.compile().params
        except CompileError:
            params = {}
        vals = {
            name: value
            for name, value in params.items()
            if (
                name not in insert.table.primary_key
                and name in insert.table.columns
                and value is not None
            )
        }
        if vals:
            insert._post_values_clause = postgresql.dml.OnConflictDoUpdate(
                index_elements=insert.table.primary_key, set_=vals
            )
        else:
            action = "do-nothing"
    if action == "do-nothing":
        insert._post_values_clause = postgresql.dml.OnConflictDoNothing(
            index_elements=insert.table.primary_key
        )
    return compiler.visit_insert(insert, **kw)
