-- Create event trigger to log schema changes ...
SELECT pgmemento.create_schema_event_trigger(TRUE);

SELECT pgmemento.init(
  'public',
  'pgmemento_audit_id',
  -- Log existing data as imported
  TRUE,
  -- Log new data
  FALSE,
  -- Log "state" (not sure what this is)
  FALSE,
  -- Trigger create tables (add on new tables...)
  FALSE,
  -- Tables to ignore
  ARRAY['spatial_ref_sys']
);

-- Reinit to capture changes to audit approach.
-- Start auditing for tables in `public` schema
SELECT pgmemento.reinit(
  'public',
  'pgmemento_audit_id',
  -- Log existing data as imported
  TRUE,
  -- Log new data
  FALSE,
  -- Trigger on table creation
  FALSE,
  -- Tables to ignore
  ARRAY['spatial_ref_sys']
);

SELECT pgmemento.init(
  'geo_context'
);

SELECT pgmemento.init(
  'vocabulary'
);

SELECT pgmemento.init(
  'sparrow_defs'
);

SELECT pgmemento.init(
  'tags'
);

