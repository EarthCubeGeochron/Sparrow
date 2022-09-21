from sparrow.database.migration import SparrowMigration, has_column, has_table
from sparrow.database import run_sql
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
            stop_on_error=True,
        )


class DocumentTriggerMigration(SparrowMigration):
    name = "remove-document-triggers"

    def apply(self, db):
        run_sql(
            db.session,
            """
drop trigger if exists "log_delete_trigger" on "documents"."project_document";
drop trigger if exists "log_insert_trigger" on "documents"."project_document";
drop trigger if exists "log_transaction_trigger" on "documents"."project_document";
drop trigger if exists "log_truncate_trigger" on "documents"."project_document";
drop trigger if exists "log_update_trigger" on "documents"."project_document";
drop trigger if exists "log_delete_trigger" on "documents"."sample_document";
drop trigger if exists "log_insert_trigger" on "documents"."sample_document";
drop trigger if exists "log_transaction_trigger" on "documents"."sample_document";
drop trigger if exists "log_truncate_trigger" on "documents"."sample_document";
drop trigger if exists "log_update_trigger" on "documents"."sample_document";
drop trigger if exists "log_delete_trigger" on "documents"."session_document";
drop trigger if exists "log_insert_trigger" on "documents"."session_document";
drop trigger if exists "log_transaction_trigger" on "documents"."session_document";
drop trigger if exists "log_truncate_trigger" on "documents"."session_document";
drop trigger if exists "log_update_trigger" on "documents"."session_document";
drop trigger if exists "log_delete_trigger" on "sparrow_defs"."organization";
drop trigger if exists "log_insert_trigger" on "sparrow_defs"."organization";
drop trigger if exists "log_transaction_trigger" on "sparrow_defs"."organization";
drop trigger if exists "log_truncate_trigger" on "sparrow_defs"."organization";
drop trigger if exists "log_update_trigger" on "sparrow_defs"."organization";
drop trigger if exists "log_delete_trigger" on "tile_utils"."tms_definition";
drop trigger if exists "log_insert_trigger" on "tile_utils"."tms_definition";
drop trigger if exists "log_transaction_trigger" on "tile_utils"."tms_definition";
drop trigger if exists "log_truncate_trigger" on "tile_utils"."tms_definition";
drop trigger if exists "log_update_trigger" on "tile_utils"."tms_definition";
alter table "documents"."project_document" drop constraint
"project_document_audit_id_key";
alter table "documents"."sample_document" drop constraint
"sample_document_audit_id_key";
alter table "documents"."session_document" drop constraint
"session_document_audit_id_key";
alter table "sparrow_defs"."organization" drop constraint "organization_audit_id_key";
drop index if exists "documents"."project_document_audit_id_key";
drop index if exists "documents"."sample_document_audit_id_key";
drop index if exists "documents"."session_document_audit_id_key";
drop index if exists "sparrow_defs"."organization_audit_id_key";
alter table "documents"."project_document" drop column "audit_id";
alter table "documents"."sample_document" drop column "audit_id";
alter table "documents"."session_document" drop column "audit_id";
alter table "sparrow_defs"."organization" drop column "audit_id";
        """,
        )
