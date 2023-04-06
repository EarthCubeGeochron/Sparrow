SELECT pgmemento.drop_schema_event_trigger();

SELECT
  pgmemento.drop_table_audit(
    quote_ident(table_name),
    quote_ident(schema_name),
    FALSE
  )
FROM
  pgmemento.audit_table_log
WHERE
  upper(txid_range) IS NULL
  AND lower(txid_range) IS NOT NULL;

drop trigger if exists "log_transaction_trigger" on "public"."user";
drop index if exists "pgmemento"."transaction_log_date_idx";
drop index if exists "pgmemento"."transaction_log_unique_idx_2";
drop index if exists "pgmemento"."transaction_log_unique_idx";

DROP SCHEMA pgmemento;
