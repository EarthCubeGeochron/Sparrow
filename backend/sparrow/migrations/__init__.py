from sqlalchemy.exc import DataError
from macrostrat.dinosaur import SchemaMigration, has_column, has_table
from sparrow.database import run_sql
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from sqlalchemy import text


class PlateauMigration(SchemaMigration):
    name = "remove-in-plateau"

    def should_apply(self, source, target, migrator):
        args = ('"public"."session"', "in_plateau")
        return has_column(source, *args) and not has_column(target, *args)

    def apply(self, engine):
        with engine.connect() as conn:
            conn.execute("ALTER TABLE session DROP COLUMN in_plateau")


class InstrumentSessionMigration(SchemaMigration):
    name = "add-instrument-session"

    def should_apply(self, source, target, migrator):
        pub = '"public"."instrument_session"'
        return has_table(target, pub) and not has_table(source, pub)

    def apply(self, engine):
        ix = "data_file_link_file_hash_session_id_analysis_id_sample_id_key"
        run_sql(
            engine,
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

    def apply(self, engine):
        sess = sessionmaker(bind=engine)()
        run_sql(sess, "ALTER TABLE sample DROP CONSTRAINT sample_check")


class SampleLocationAddSRID(SchemaMigration):
    name = "add-srid-to-sample-location"

    def should_apply(self, source, target, migrator):
        sql = "SELECT srid FROM geometry_columns WHERE f_table_name = 'sample' AND f_geometry_column = 'location'"
        res = run_sql(source, sql)[0].fetchone()
        return res is None or res[0] != 4326

    def apply(self, engine):
        try:
            sql_file = Path(__file__).parent / "sql" / "add-sample-srid.sql"
            run_sql(engine, sql_file)
        except DataError:
            pass


class SampleAttributeCascadeMigration(SchemaMigration):
    name = "sample-attribute-cascade"

    def should_apply(self, source, target, migrator):
        """If there are no foreign key cascades on __sample_attribute"""
        sql = """SELECT count(*) = 0 FROM pg_constraint
        WHERE conrelid = '__analysis_attribute'::regclass
        AND pg_get_constraintdef(oid) ILIKE '%ON DELETE CASCADE%'
        """
        with source.connect() as conn:
            res = conn.execute(text(sql)).fetchone()
            return res[0]

    def apply(self, engine):
        try:
            sql_file = Path(__file__).parent / "sql" / "add-sample-delete-cascades.sql"
            list(run_sql(engine, sql_file))
        except DataError:
            pass
