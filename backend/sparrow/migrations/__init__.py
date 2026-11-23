"""
Migrations for changes that a schema diff cannot make safely. Each states what
holds before and after it runs, so its status is read from the database.
"""

from pathlib import Path

from macrostrat.schema_management import any_of, exists, has_columns, negate

from sparrow.database.migration import SparrowMigration, has_constraint, query_is_true

sql = Path(__file__).parent / "sql"


class PlateauMigration(SparrowMigration):
    name = "remove-in-plateau"
    destructive = True
    preconditions = [has_columns("public", "analysis", "in_plateau")]
    postconditions = [negate(has_columns("public", "analysis", "in_plateau"))]

    def apply(self, db):
        db.run_sql("ALTER TABLE analysis DROP COLUMN in_plateau")


_data_file_link_key = "data_file_link_file_hash_session_id_analysis_id_sample_id_key"


class InstrumentSessionMigration(SparrowMigration):
    name = "add-instrument-session"
    preconditions = [has_constraint("public.data_file_link", _data_file_link_key)]
    postconditions = [
        negate(has_constraint("public.data_file_link", _data_file_link_key))
    ]

    def apply(self, db):
        db.run_sql(
            f"""
        ALTER TABLE data_file_link DROP CONSTRAINT {_data_file_link_key};
        ALTER TABLE data_file_link DROP CONSTRAINT data_file_link_check;
        DROP INDEX IF EXISTS {_data_file_link_key};
        """
        )


class SampleCheckMigration(SparrowMigration):
    """The check constraint on samples changed when `lab_id` was added."""

    name = "add-sample-check"
    preconditions = [
        exists("public", "sample"),
        has_constraint("public.sample", "sample_check"),
    ]
    postconditions = [
        any_of(
            [
                has_columns("public", "sample", "lab_id"),
                negate(has_constraint("public.sample", "sample_check")),
            ]
        )
    ]

    def apply(self, db):
        db.run_sql("ALTER TABLE sample DROP CONSTRAINT sample_check")


class SampleLocationAddSRID(SparrowMigration):
    name = "add-srid-to-sample-location"
    preconditions = [has_columns("public", "sample", "location")]
    postconditions = [
        query_is_true(
            """SELECT srid = 4326 FROM geometry_columns
            WHERE f_table_schema = 'public'
              AND f_table_name = 'sample'
              AND f_geometry_column = 'location'"""
        )
    ]

    def apply(self, db):
        db.run_sql(sql / "add-sample-srid.sql")


class SampleAttributeCascadeMigration(SparrowMigration):
    name = "sample-attribute-cascade"
    preconditions = [exists("public", "__analysis_attribute")]
    postconditions = [
        query_is_true(
            """SELECT count(*) > 0 FROM pg_constraint
            WHERE conrelid = '__analysis_attribute'::regclass
              AND confdeltype = 'c'"""
        )
    ]

    def apply(self, db):
        db.run_sql(sql / "add-sample-delete-cascades.sql")


core_migrations = [
    PlateauMigration,
    InstrumentSessionMigration,
    SampleCheckMigration,
    SampleLocationAddSRID,
    SampleAttributeCascadeMigration,
]
