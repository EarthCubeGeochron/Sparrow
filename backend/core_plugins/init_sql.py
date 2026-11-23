from os import environ
from pathlib import Path

from macrostrat.schema_management import SchemaDefinition

from sparrow.core.plugins import SparrowCorePlugin


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

    def on_define_schema(self, chunks):
        """A lab's own schema extensions, applied after everything built in"""
        if self.init_sql is None:
            return
        chunks.append(
            SchemaDefinition(
                name="init-sql",
                depends_on=[c.name for c in chunks],
                provides=sorted(self.init_sql),
            )
        )
