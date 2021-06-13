from .database.migration import SparrowMigration, has_column, has_table
from .database.util import run_sql
from sqlalchemy.orm import sessionmaker
from schemainspect import get_inspector


class PlateauMigration(SparrowMigration):
    name = "remove-in-plateau"

    def should_apply(self, source, target, migrator):
        args = ('"public"."session"', "in_plateau")
        return has_column(source, *args) and not has_column(target, *args)

    def apply(self, db):
        db.engine.execute("ALTER TABLE analysis DROP COLUMN in_plateau")


class InstrumentSessionMigration(SparrowMigration):
    name = "add-instrument-session"

    def should_apply(self, source, target, migrator):
        pub = '"public"."instrument_session"'
        return not has_table(source, pub) and has_table(target, pub)

    def apply(self, db):
        ix = "data_file_link_file_hash_session_id_analysis_id_sample_id_key"
        sess = sessionmaker(bind=db.engine)()
        run_sql(
            sess,
            f"""
        ALTER TABLE data_file_link DROP CONSTRAINT {ix};
        ALTER TABLE data_file_link DROP CONSTRAINT data_file_link_check;
        DROP INDEX IF EXISTS {ix};
        """,
        )
