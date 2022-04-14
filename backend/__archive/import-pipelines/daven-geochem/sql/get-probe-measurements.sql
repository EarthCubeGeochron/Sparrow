SELECT
  id,
  line_number,
  mineral,
  sample_id,
  session_id,
  cr_number,
  mg_number,
  oxide_total,
  spot_size,
  geometry AS location
FROM probe_measurement
