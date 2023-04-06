from macrostrat.dinosaur import SchemaMigration, AutoMigration
from sqlalchemy import inspect, sql
from sparrow.core.plugins import SparrowCorePlugin
from macrostrat.utils import relative_path, cmd
from sparrow.core import get_database
import click
from pathlib import Path
from sqlalchemy.exc import ProgrammingError
from sparrow.database import Database
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
    procedures = [
        "pg-memento/ctl/UPGRADE",
        "pg-memento/UPGRADE_v061_to_v07",
        "pg-memento/UPGRADE_v07_to_v074",
    ]

    args = connection_args(engine)
    print(args)
    for _id in procedures:
        print("Running PGMemento procedure", _id)
        fp = relative_path(__file__, _id + ".sql")
        run_psql(engine, fp)


def run_psql(engine, fp):
    args = connection_args(engine)
    cmd(f"psql -f {fp}", *args, cwd=Path(__file__).parent)


def get_procedure(name):
    sql = relative_path(__file__, "procedures", name + ".sql")
    return open(sql).read()


def get_old_triggers(engine):
    """
    Get the old triggers that need to be dropped
    """
    return engine.execute(get_procedure("get-old-triggers")).fetchall()


def get_old_audit_id(engine):
    return engine.execute(get_procedure("get-old-audit-id")).fetchall()


class PGMementoMigration(SchemaMigration):
    """Migrate audit logging to version 0.7.4 from the 0.6 series"""

    name = "document-table-migration"
    target = None

    def should_apply(self, source, target, migrator):
        db = Database(source.url)
        old_triggers = get_old_triggers(db.session)
        old_audit_id = get_old_audit_id(db.session)
        return (
            has_audit_id(source, "public", "sample", col_name="audit_id")
            and len(old_triggers) > 0
            and len(old_audit_id) > 0
        )

    def apply(self, engine):
        db = Database(engine.url)
        upgrade_audit_trail(engine)
        # A scorched-earth approach to dropping the v1 audit trail
        db.session.execute("DROP SCHEMA IF EXISTS core_view CASCADE")

        sql = ""
        for trigger in get_old_triggers(db.session):
            for op in ["insert", "update", "delete", "truncate"]:
                sql += f"DROP TRIGGER IF EXISTS log_{op}_trigger ON {trigger.schema}.{trigger.table} CASCADE;\n"
        for audit_id in get_old_audit_id(db.session):
            sql += f"ALTER TABLE {audit_id.schema}.{audit_id.table} DROP COLUMN audit_id CASCADE;\n"
        run_sql(db.session, sql)
        db.session.commit()
        db.exec_sql(relative_path(__file__, "drop-audit.sql"))

        build_audit_tables(db)

        db.recreate_views()

        # migration = AutoMigration(engine, self.target)
        # migration.add_all_changes()
        # stmts = migration.statements
        # print(stmts)
        # raise
        # for stmt in stmts:
        #     _stmt = stmt.lower()
        #     if (
        #         _stmt.startswith("alter table")
        #         and "drop constraint" in _stmt
        #         and "audit_id" in _stmt
        #     ):
        #         engine.execute(stmt.replace(";", " CASCADE;"))
        #     if "drop column" in _stmt and "audit_id" in _stmt:
        #         engine.execute(stmt)


class PGMemento074Migration(SchemaMigration):
    """
    Migrate PGMemento to a bugfix release to handle PostgreSQL 15.
    This migration only runs if we are on version 0.7.3.
    """

    def should_apply(self, source, target, migrator):
        # Get the version of PGMemento
        try:
            version = source.execute(
                "SELECT major_version, minor_version, revision FROM pgmemento.version()"
            ).scalar()
        except ProgrammingError:
            return False
        # Parse version string
        print(version)
        return (
            version.major_version == 0
            and version.minor_version == 7
            and version.revision < 4
        )

    def apply(self, engine):
        fp = relative_path(__file__, "pg-memento/UPGRADE_v07_to_v074.sql")
        run_psql(engine, fp)
        db = Database(engine.url)
        db.initialize()


def build_audit_tables(db):
    procedures = []

    if not has_audit_schema(db):
        # Create the schema to hold audited tables
        # NOTE: this drops all transaction history, so we don't run
        # it if pgMemento tables already exist.
        procedures.append("SCHEMA")

    # Basic setup procedures
    procedures += [
        "SETUP",
        "SETUP",  # Run twice to ensure all tables are created
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


class VersioningPlugin(SparrowCorePlugin):
    name = "versioning"

    def on_finalize_database_schema(self, db):
        build_audit_tables(db)

    def on_setup_cli(self, cli):
        cli.add_command(drop_audit_trail)

    def on_prepare_database_migrations(self, migrator):
        migrator.add_migration(PGMementoMigration)
        migrator.add_migration(PGMemento074Migration)
