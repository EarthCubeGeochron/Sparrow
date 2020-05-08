-- Create event trigger to log schema changes ...
SELECT pgmemento.create_schema_event_trigger(TRUE);

-- Start auditing for tables in `public` schema
SELECT pgmemento.create_schema_audit(
  'public',
  -- Log existing data as imported
  FALSE,
  -- Tables to ignore
  ARRAY['spatial_ref_sys']
);

SELECT pgmemento.create_schema_audit(
  'geo_context',
  -- Log existing data as imported
  FALSE,
  -- Tables to ignore
  null
);

SELECT pgmemento.create_schema_audit(
  'vocabulary',
  -- Log existing data as imported
  FALSE,
  -- Tables to ignore
  null
);
