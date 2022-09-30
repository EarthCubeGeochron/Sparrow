-- Create event trigger to log schema changes ...
SELECT pgmemento.create_schema_event_trigger(TRUE);

-- Start auditing for tables in `public` schema
SELECT pgmemento.init(
  'public',
  'pgmemento_audit_id',
  -- Log existing data as imported
  FALSE,
  -- Log new data
  FALSE,
  FALSE,
  TRUE,
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

