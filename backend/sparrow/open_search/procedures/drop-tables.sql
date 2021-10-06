/*
A procedure to run at initialization if the document tables are empty. 
*/

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
alter table "documents"."project_document" drop constraint
"project_document_audit_id_key";
alter table "documents"."sample_document" drop constraint
"sample_document_audit_id_key";
alter table "documents"."session_document" drop constraint
"session_document_audit_id_key";
drop index if exists "documents"."project_document_audit_id_key";
drop index if exists "documents"."sample_document_audit_id_key";
drop index if exists "documents"."session_document_audit_id_key";
alter table "documents"."project_document" drop column "audit_id";
alter table "documents"."sample_document" drop column "audit_id";
alter table "documents"."session_document" drop column "audit_id";