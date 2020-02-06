from sqlalchemy import inspect, sql
from sparrow.plugins import SparrowCorePlugin
from sparrow.util import relative_path
from sparrow import App
import click
from sparrow.util import run_sql

exclude_tables = ['spatial_ref_sys']
audit_schemas = ['public', 'vocabulary']

def has_audit_id(db, schema, table):
    insp = inspect(db.engine)
    cols = insp.get_columns(table, schema=schema)
    col_names = [c['name'] for c in cols]
    return 'audit_id' in col_names

def audit_tables(db):
    insp = inspect(db.engine)
    for schema in audit_schemas:
        for table in insp.get_table_names(schema=schema):
            if table in exclude_tables:
                continue
            if not has_audit_id(db, schema, table):
                continue
            yield schema, table

def drop_audit_columns(db):
    for schema, table in audit_tables(db):
        q = f"ALTER TABLE {schema}.{table} DROP COLUMN audit_id CASCADE"
        run_sql(db.session, q)

# There is a bug where audit-trail columns
# lose default values, causing INSERTS to be rejected
# across-the-board...
# This appears to happen on schema setup.
# May need to reapply defaults to audit columns:
# ALTER COLUMN audit_id SET DEFAULT
#   nextval(''pgmemento.audit_id_seq''::regclass)
def add_audit_id_sequence(db):
    for schema, table in audit_tables(db):
        q = (f"ALTER TABLE {schema}.{table} "
             "ALTER COLUMN audit_id SET DEFAULT "
             "nextval('pgmemento.audit_id_seq'::regclass)")
        run_sql(db.session, q)

@click.command(name="remove-audit-trail")
def drop_audit_trail():
    """
    Remove PGMemento audit trail
    """
    db = App(__name__).database
    db.exec_sql(relative_path(__file__, 'drop-audit.sql'))
    drop_audit_columns(db)

class VersioningPlugin(SparrowCorePlugin):
    name = "versioning"
    def on_core_tables_initialized(self, db):
        files = [
            "src/SCHEMA.sql",
            "src/SETUP.sql",
            "src/LOG_UTIL.sql",
            "src/DDL_LOG.sql",
            "src/RESTORE.sql",
            "src/REVERT.sql",
            "src/SCHEMA_MANAGEMENT.sql"
        ]
        for fn in files:
            fp = relative_path(__file__, 'pg-memento', fn)
            db.exec_sql(fp)
        db.exec_sql(relative_path(__file__,'start-logging.sql'))
        add_audit_id_sequence(db)

    def on_setup_cli(self, cli):
        cli.add_command(drop_audit_trail)
