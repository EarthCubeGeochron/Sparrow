from sparrow.plugins import SparrowCorePlugin
from os import environ
from pathlib import Path
from click import secho


class InitSQLPlugin(SparrowCorePlugin):
    name = "init-sql"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Schema extensions
        self.init_sql = None
        sql = environ.get("SPARROW_INIT_SQL", None)
        if sql is not None:
            p = Path(sql)
            assert p.exists()
            if p.is_dir():
                files = p.glob("*.sql")
            else:
                files = [p]
            self.init_sql = [f for f in files if f.is_file()]

    def on_core_tables_initialized(self, db):
        if self.init_sql is None:
            return
        secho("\nInitializing schema extensions", bold=True)
        for s in self.init_sql:
            db.exec_sql(s)
