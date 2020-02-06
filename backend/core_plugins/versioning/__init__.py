from sparrow.plugins import SparrowCorePlugin
from sparrow.util import relative_path
from sparrow import App
import click
from sqlalchemy import inspect, sql
from sparrow.util import run_sql

exclude_tables = ['spatial_ref_sys']

@click.command(name="remove-audit-trail")
def drop_audit_trail():
    """
    Remove PGMemento audit trail
    """
    db = App(__name__).database
    db.exec_sql(relative_path(__file__, 'drop-audit.sql'))
    insp = inspect(db.engine)
    for table in insp.get_table_names(schema='public'):
        if table in exclude_tables:
            continue
        cols = insp.get_columns(table, schema='public')
        col_names = [c['name'] for c in cols]
        if 'audit_id' not in col_names:
            continue
        q = f"ALTER TABLE {table} DROP COLUMN audit_id CASCADE"
        run_sql(db.session, q)

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

    def on_setup_cli(self, cli):
        cli.add_command(drop_audit_trail)
