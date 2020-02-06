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

DROP SCHEMA pgmemento CASCADE;
