drop index if exists "pgmemento"."transaction_log_date_idx";
drop index if exists "pgmemento"."transaction_log_unique_idx_2";
drop index if exists "pgmemento"."transaction_log_unique_idx";
drop table if exists "pgmemento"."audit_tables_copy";