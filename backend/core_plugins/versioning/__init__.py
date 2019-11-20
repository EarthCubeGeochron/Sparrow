from sparrow.plugins import SparrowCorePlugin
from sparrow.util import relative_path

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
