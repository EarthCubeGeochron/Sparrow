"""
Sparrow's database schema, described for `macrostrat.schema_management`.

The schema is a set of chunks: the core fixtures, then whatever plugins add.
A plan is the difference between a lab's database and those chunks built into
an empty database on the same server.
"""

from contextlib import contextmanager
from os import environ
from pathlib import Path
from tempfile import gettempdir

from macrostrat.database.utils import temporary_database
from macrostrat.schema_management import (
    MigrationRunner,
    SchemaApp,
    SchemaDefinition,
    apply_sql_path,
    build_schema,
)
from macrostrat.schema_management.plan import StatementCounter, is_unsafe_statement
from sqlparse import format as format_sql

from sparrow.logs import get_logger

log = get_logger(__name__)

fixtures = Path(__file__).parent / "fixtures"


class SchemaUpdateError(Exception):
    """The schema could not be brought up to date automatically."""

    def __init__(self, message, statements=None):
        super().__init__(message)
        self.statements = statements or []


def core_chunk() -> SchemaDefinition:
    return SchemaDefinition(name="core", provides=[fixtures])


def schema_chunks(app) -> list[SchemaDefinition]:
    """The chunks of Sparrow's schema, including those defined by plugins."""
    chunks = [core_chunk()]
    if app is None:
        return chunks

    app.run_hook("define-schema", chunks)

    def _depends_on_all():
        return [c.name for c in chunks]

    # Plugins written before schema chunks add tables in these hooks
    chunks.append(
        SchemaDefinition(
            name="plugin-hooks",
            depends_on=_depends_on_all(),
            provides=[lambda db: app.run_hook("core-tables-initialized", db)],
        )
    )
    chunks.append(
        SchemaDefinition(
            name="finalize",
            depends_on=_depends_on_all(),
            provides=[lambda db: app.run_hook("finalize-database-schema", db)],
        )
    )
    return chunks


def schema_migrations(app) -> list[type]:
    from sparrow import migrations

    classes = list(migrations.core_migrations)
    if app is not None:
        app.run_hook("define-migrations", classes)
    return classes


def _environment_class():
    if environ.get("SPARROW_ENV", "production") == "development":
        return "development"
    return "production"


def _planning_url(db):
    return db.engine.url.set(database=db.engine.url.database + "_schema_plan")


def create_schema_app(db, **kwargs) -> SchemaApp:
    """Describe a Sparrow database to the schema management tools."""
    from . import Database

    app = db.app

    @contextmanager
    def planning_database():
        # A sibling database, since the backend cannot start containers
        with temporary_database(_planning_url(db), ensure_empty=True) as engine:
            plan_db = Database(engine.url, app)
            try:
                yield plan_db
            finally:
                plan_db.cleanup()

    schema_dir = Path(
        environ.get("SPARROW_SCHEMA_DIR", Path(gettempdir()) / "sparrow-schema")
    )

    kwargs.setdefault("env_class", _environment_class())
    return SchemaApp(
        name="sparrow",
        database=lambda: db,
        chunks=schema_chunks(app),
        schema_dir=schema_dir,
        migrations=schema_migrations(app),
        environment=environ.get("SPARROW_LAB_NAME", "sparrow"),
        planning_database=planning_database,
        after_change=lambda _db: _db.reload_postgrest_cache(),
        source_root=Path(__file__).parent.parent.parent,
        **kwargs,
    )


def initialize_schema(db):
    """Build the full schema into a database."""
    build_schema(db, schema_chunks(db.app))


def _is_comment(statement, params=None):
    return (
        format_sql(statement, strip_comments=True)
        .lstrip()
        .upper()
        .startswith("COMMENT ON")
    )


def sync_comments(db, chunks):
    """Re-apply comments, which a view loses when a diff recreates it."""
    for chunk in chunks:
        for provider in chunk.provides:
            if isinstance(provider, Path):
                apply_sql_path(db, provider, statement_filter=_is_comment)


def run_migrations(db, schema_app: SchemaApp):
    """Apply migrations until none can apply; lab databases have no ledger."""
    runner: MigrationRunner = schema_app.runner(db)
    return runner.run_to_completion(raise_errors=True)


def update_schema(db, apply=True):
    """Bring a database up to date: migrations, the schema's own statements,
    the schema diff, then the views, functions, seed data and grants a diff
    cannot manage.

    Statements that could lose data are never applied. If any remain, the
    update fails so that they can be handled by a migration or by hand.
    """
    schema_app = create_schema_app(db)
    run_migrations(db, schema_app)

    # Statements that already hold fail and are stepped over; this replaces
    # functions and triggers (notably the audit trail's) before tables change.
    initialize_schema(db)
    schema_app.changed(db)

    plan_file, statements = schema_app.write_plan()
    unsafe = [s for s in statements if is_unsafe_statement(s)]
    if unsafe:
        raise SchemaUpdateError(
            f"{len(unsafe)} schema changes could lose data and were not applied", unsafe
        )
    log.info(f"Schema plan has {len(statements)} statements")
    if not apply:
        return statements

    counter: StatementCounter = schema_app.apply_plan(
        plan_file, safe=True, assume_yes=True
    )
    counter.print_report()
    # Views are left as the diff made them: re-running their definitions would
    # reorder columns selected with `*` on databases older than the schema.
    schema_app.sync(assume_yes=True, views=False)
    sync_comments(db, schema_app.environment_chunks())
    schema_app.changed(db)
    return statements
