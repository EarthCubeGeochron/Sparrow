from pathlib import Path

from macrostrat.database.utils import run_sql_file
from macrostrat.schema_management import SchemaDefinition, has_columns, negate
from sqlalchemy import text

from sparrow import core
from sparrow.core.plugins import SparrowCorePlugin
from sparrow.core.task_manager.base import task
from sparrow.database.migration import SparrowMigration

from .base import OpenSearchAPI

here = Path(__file__).parent
fixtures = here / "fixtures"
procedures = here / "procedures"


def _initialize_tables(engine, refresh=True):
    fill_empty_docs = procedures / "fill_empty_tables.sql"
    if refresh:
        run_sql_file(engine, procedures / "drop-tables.sql")

    filenames = list(fixtures.glob("*.sql"))
    filenames.sort()

    # creates tables, functions, triggers and indexes
    for fn in filenames:
        run_sql_file(engine, fn)

    # checks if tables are empty, if so try to fill with info from other tables
    run_sql_file(engine, fill_empty_docs)


class DocumentTableMigration(SparrowMigration):
    """Remove unintentional application of schema versioning."""

    name = "document-table-migration"
    subsystem = "open-search"
    preconditions = [has_columns("documents", "project_document", "audit_id")]
    postconditions = [negate(has_columns("documents", "project_document", "audit_id"))]

    def apply(self, db):
        _initialize_tables(db.engine, refresh=True)
        run_sql_file(db.engine, procedures / "drop-extra-triggers.sql")


class OpenSearch(SparrowCorePlugin):
    name = "open-search"

    def initialize_tables(self, db, refresh=True):
        _initialize_tables(db.engine, refresh)

    def on_define_schema(self, chunks):
        chunks.append(
            SchemaDefinition(
                name="open-search",
                depends_on=["core"],
                provides=[
                    fixtures,
                    # Fill empty document tables from the tables they index
                    lambda db: db.run_sql(procedures / "fill_empty_tables.sql"),
                ],
            )
        )

    def on_api_initialized_v2(self, api):
        api.mount("/search", OpenSearchAPI, name=self.name)

    def on_define_migrations(self, migrations):
        migrations.append(DocumentTableMigration)


@task(name="refresh-search-index")
def refresh_search_triggers():
    """Refresh open search triggers in case they get out of sync."""
    db = core.get_database()
    open_search = core.get_plugin("open-search")
    open_search.initialize_tables(db)
