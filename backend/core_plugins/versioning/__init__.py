from macrostrat.dinosaur import SchemaMigration
from sqlalchemy import inspect, sql
from sparrow.core.plugins import SparrowCorePlugin
from macrostrat.utils import relative_path, cmd
from sparrow.core import get_database
import click
from pathlib import Path

from macrostrat.database.utils import connection_args, run_sql

exclude_tables = ["spatial_ref_sys"]
audit_schemas = ["public", "vocabulary", "tags", "geo_context"]

# Tables in the pg_memento schema
memento_tables = [
    "audit_schema_log",
    "audit_column_log",
    "audit_table_log",
    "table_event_log",
    "transaction_log",
    "row_log",
]


def has_audit_id(db, schema, table, col_name="pgmemento_audit_id"):
    insp = inspect(db.engine)
    cols = insp.get_columns(table, schema=schema)
    col_names = [c["name"] for c in cols]
    return col_name in col_names


def audit_tables(db):
    insp = inspect(db.engine)
    for schema in audit_schemas:
        for table in insp.get_table_names(schema=schema):
            if table in exclude_tables:
                continue
            if not has_audit_id(db, schema, table):
                continue
            yield schema, table


def has_audit_schema(db):
    insp = inspect(db.engine)
    realized_tables = insp.get_table_names(schema="pgmemento")
    # Some of the pg_memento tables are not created...
    return all(t in realized_tables for t in memento_tables)


def drop_audit_columns(db):
    for schema, table in audit_tables(db):
        q = f"ALTER TABLE {schema}.{table} DROP COLUMN pgmemento_audit_id CASCADE"
        run_sql(db.session, q)


def add_audit_id_sequence(db):
    """
    Re-add audit sequences (this seems necessary sometimes)
    """
    for schema, table in audit_tables(db):
        q = (
            f"ALTER TABLE {schema}.{table} "
            "ALTER COLUMN pgmemento_audit_id SET DEFAULT "
            "nextval('pgmemento.audit_id_seq'::regclass)"
        )
        run_sql(db.session, q)


@click.command(name="remove-audit-trail")
def drop_audit_trail():
    """
    Remove PGMemento audit trail
    """
    db = get_database()
    db.exec_sql(relative_path(__file__, "drop-audit.sql"))
    drop_audit_columns(db)


def upgrade_audit_trail(engine):
    """
    Upgrade PGMemento audit trail
    """
    procedures = ["UPGRADE_v060_to_v061", "UPGRADE_v061_to_v07", "UPGRADE_v07_to_v073"]

    args = connection_args(engine)
    print(args)
    for id in procedures:
        fp = relative_path(__file__, "pg-memento", id + ".sql")
        cmd(f"psql -f {fp}", *args, cwd=Path(__file__).parent)


class PGMementoMigration(SchemaMigration):
    """Migrate audit logging to version 0.7.3"""

    name = "document-table-migration"

    def should_apply(self, source, target, migrator):
        return has_audit_id(source, "public", "sample", col_name="audit_id")

    def apply(self, engine):
        upgrade_audit_trail(engine)


class VersioningPlugin(SparrowCorePlugin):
    name = "versioning"

    def proc(self, id):
        fn = id + ".sql"
        return

    def on_finalize_database_schema(self, db):

        procedures = []

        if not has_audit_schema(db):
            # Create the schema to hold audited tables
            # NOTE: this drops all transaction history, so we don't run
            # it if pgMemento tables already exist.
            procedures.append("SCHEMA")

        # Basic setup procedures
        procedures += [
            "SETUP",
            "LOG_UTIL",
            "DDL_LOG",
            "RESTORE",
            "REVERT",
            "SCHEMA_MANAGEMENT",
            "CTL",
        ]

        for id in procedures:
            fp = relative_path(__file__, "pg-memento", "src", id + ".sql")
            db.exec_sql(fp)
        db.exec_sql(relative_path(__file__, "start-logging.sql"))

    def on_setup_cli(self, cli):
        cli.add_command(drop_audit_trail)
        cli.add_command(upgrade_audit_trail)

    def on_prepare_database_migrations(self, migrator):
        migrator.add_migration(PGMementoMigration)
