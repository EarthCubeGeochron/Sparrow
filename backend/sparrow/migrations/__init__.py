from sqlalchemy.exc import DataError
from macrostrat.dinosaur import SchemaMigration, has_column, has_table
from sparrow.database import run_sql
from sqlalchemy.orm import sessionmaker
from pathlib import Path


class PlateauMigration(SchemaMigration):
    name = "remove-in-plateau"

    def should_apply(self, source, target, migrator):
        args = ('"public"."session"', "in_plateau")
        return has_column(source, *args) and not has_column(target, *args)

    def apply(self, db):
        db.engine.execute("ALTER TABLE analysis DROP COLUMN in_plateau")


class InstrumentSessionMigration(SchemaMigration):
    name = "add-instrument-session"

    def should_apply(self, source, target, migrator):
        pub = '"public"."instrument_session"'
        return has_table(target, pub)

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


class SampleCheckMigration(SchemaMigration):
    name = "add-sample-check"

    def should_apply(self, source, target, migrator):
        pub = '"public"."sample"'
        return not has_column(source, pub, "lab_id")

    def apply(self, db):
        sess = sessionmaker(bind=db.engine)()
        run_sql(sess, "ALTER TABLE sample DROP CONSTRAINT sample_check")


class SampleLocationAddSRID(SchemaMigration):
    name = "add-srid-to-sample-location"

    def should_apply(self, source, target, migrator):
        sql = "SELECT srid FROM geometry_columns WHERE f_table_name = 'sample' AND f_geometry_column = 'location'"
        res = source.execute(sql).fetchone()
        return res is None or res[0] != 4326

    def apply(self, engine):
        try:
            sql_file = Path(__file__).parent / "sql" / "add-sample-srid.sql"
            engine.execute(sql_file.read_text())
        except DataError:
            pass
