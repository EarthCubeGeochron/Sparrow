from pathlib import Path
from sqlalchemy import text
import sparrow
from sparrow.plugins import SparrowCorePlugin
from sparrow.task_manager.base import task
from sparrow.database.migration import SparrowMigration, has_column
from sparrow.database.util import run_sql_file

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

    #creates tables, functions, triggers and indexes
    for fn in filenames:
        run_sql_file(engine, fn)

    # checks if tables are empty, if so try to fill with info from other tables
    run_sql_file(engine, fill_empty_docs)


class DocumentTableMigration(SparrowMigration):
    """Remove unintentional application of schema versioning."""

    name = "document-table-migration"

    def should_apply(self, source, target, migrator):
        args = ('"documents"."project_document"', "audit_id")
        return has_column(source, *args) and not has_column(target, *args)

    def apply(self, engine):
        _initialize_tables(engine, refresh=True)


class OpenSearch(SparrowCorePlugin):
    name = "open-search"

    def initialize_tables(self, db, refresh=True):
        _initialize_tables(db.engine, refresh)

    def on_core_tables_initialized(self, db):
        """Initialize tables on sparrow init"""
        self.initialize_tables(db)

    def on_api_initialized_v2(self, api):
        api.mount("/search", OpenSearchAPI, name=self.name)

    def on_prepare_database_migrations(self, migrator):
        migrator.add_migration(DocumentTableMigration)


@task(name="refresh-search-index")
def refresh_search_triggers():
    """Refresh open search triggers in case they get out of sync."""
    db = sparrow.get_database()
    open_search = sparrow.get_plugin("open-search")
    open_search.initialize_tables(db)
