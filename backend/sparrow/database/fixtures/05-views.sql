-- TODO: Don't cascade when we become more stable
DROP SCHEMA IF EXISTS core_view CASCADE;
CREATE SCHEMA core_view;

/* Nested list of materials, ordered from
   most specific to most general, for testing categorical
   membership of measurements */
CREATE VIEW core_view.material_tree AS
WITH RECURSIVE __r (id, type_of, hierarchy, n_levels) AS (
SELECT
  id::text,
  type_of,
  ARRAY[id]::text[] hierarchy,
  1 n_levels
FROM vocabulary.material m -- non-recursive term
UNION ALL
SELECT
  __r.id,
  m2.type_of,
  hierarchy || m2.id::text,
  n_levels + 1
FROM __r -- recursive term
JOIN vocabulary.material m2
  ON __r.type_of = m2.id
)
SELECT DISTINCT ON (id)
	id,
	hierarchy tree
FROM __r
ORDER BY id,n_levels DESC;

/* Nested list of analysis type, ordered from
   most specific to most general */
CREATE VIEW core_view.analysis_type_tree AS
WITH RECURSIVE __r (id, type_of, hierarchy, n_levels) AS (
SELECT
  id::text,
  type_of,
  ARRAY[id]::text[] hierarchy,
  1 n_levels
FROM vocabulary.analysis_type m -- non-recursive term
UNION ALL
SELECT
  __r.id,
  m2.type_of,
  hierarchy || m2.id::text,
  n_levels + 1
FROM __r -- recursive term
JOIN vocabulary.analysis_type m2
  ON __r.type_of = m2.id
)
SELECT DISTINCT ON (id)
	id,
	hierarchy tree
FROM __r
ORDER BY id,n_levels DESC;

/*
A session view with some extra features
*/
CREATE VIEW core_view.session AS
SELECT
	s.*,
	f.file_hash,
	f.type_id file_type,
	i.name instrument_name,
  ss.name sample_name,
  p.name project_name,
  is_public(s)
FROM session s
LEFT JOIN instrument i
  ON i.id = s.instrument
LEFT JOIN sample ss
  ON s.sample_id = ss.id
LEFT JOIN project p
  ON s.project_id = p.id
LEFT JOIN data_file_link l
  ON s.id = l.session_id
LEFT JOIN data_file f
  ON l.file_hash = f.file_hash
ORDER BY date DESC;

/* Analysis info with nested JSON data*/
CREATE VIEW core_view.analysis AS
WITH __a AS (
SELECT
  a.id,
  json_agg((SELECT r FROM (SELECT
  	d.id,
  	d.type,
  	d.value,
  	d.error,
  	t.unit,
  	t.parameter,
  	t.error_metric,
  	t.is_computed,
  	t.is_interpreted,
  	d.is_bad
  ) AS r)) AS data
FROM datum d
JOIN analysis a
  ON d.analysis = a.id
JOIN datum_type t
  ON d.type = t.id
GROUP BY a.id
)
SELECT
  a.id analysis_id,
  coalesce(a.date, s.date) date,
  __a.data,
  a.session_id,
  a.session_index,
  a.is_standard,
  a.is_bad,
  s.technique,
  a.analysis_type,
  ( SELECT
      name
    FROM instrument
    WHERE id = s.instrument
  ) instrument,
  ( SELECT
      tree
    FROM
      core_view.material_tree
    WHERE id = a.material
  ) material,
  ( SELECT
      tree
    FROM core_view.material_tree
    WHERE id = sa.material
  ) sample_material,
  sa.id sample_id,
  sa.igsn,
  sa.name sample_name,
  s.project_id,
  sa.location,
  is_public(s)
FROM __a
JOIN analysis a USING (id)
JOIN session s
  ON s.id = a.session_id
JOIN sample sa
  ON s.sample_id = sa.id
ORDER BY a.id;

CREATE VIEW core_view.attribute AS
SELECT
	a0.id,
	a0.parameter,
	a0.value,
	a1.id analysis_id
FROM attribute a0
JOIN __analysis_attribute aa
  ON a0.id = aa.attribute_id
JOIN analysis a1
  ON a1.id = aa.analysis_id;

CREATE VIEW core_view.datum AS
SELECT
  d.id datum_id,
  d.analysis analysis_id,
  d.type datum_type,
  d.value,
  d.error,
  t.unit,
  t.parameter,
  t.error_metric,
  t.is_computed,
  t.is_interpreted,
  d.is_bad,
  d.is_accepted,
  is_public(s),
  a.session_id,
  a.session_index,
  s.sample_id,
  sa.name sample_name,
  s.technique,
  coalesce(a.date, s.date) date
FROM datum d
JOIN analysis a
  ON d.analysis = a.id
JOIN datum_type t
  ON d.type = t.id
JOIN session s
  ON a.session_id = s.id
JOIN sample sa
  ON s.sample_id = sa.id
ORDER BY d.id;

CREATE VIEW core_view.age_datum AS
SELECT *
FROM core_view.datum
WHERE unit IN ('Ga','Ma');

CREATE VIEW core_view.material AS
SELECT id, description, authority
FROM vocabulary.material;

CREATE VIEW core_view.sample AS
SELECT DISTINCT ON (s.id)
  s.id,
  s.igsn,
  s.name,
  s.material,
  ST_AsGeoJSON(s.location)::jsonb geometry,
  s.location_name,
  s.location_precision,
  s.location_name_autoset,
  p.id project_id,
  p.name project_name,
  is_public(s)
FROM sample s
LEFT JOIN session ss
  ON s.id = ss.sample_id
LEFT JOIN project p
  ON ss.project_id = p.id;

CREATE VIEW core_view.age_context AS
SELECT
	s.id sample_id,
	ss.id session_id,
	d.id datum_id,
	s.name sample_name,
	s.material,
	ss.target,
    'Feature' AS type,
	ST_AsGeoJSON(s.location)::jsonb geometry,
	s.location_name,
	s.location_precision,
	d.value,
	d.error,
	dt.parameter,
	dt.unit,
	dt.error_unit,
	dt.error_metric,
	g.name geo_entity_name,
	g.type geo_entity_type
FROM sample s
JOIN session ss
  ON ss.sample_id = s.id
JOIN analysis a
  ON a.session_id = ss.id
JOIN datum d
  ON d.analysis = a.id
JOIN datum_type dt
  ON dt.id = d.type
/*
TODO: Because the sample_geo_entity link is many-to-one, there might be more
than one geo_entity defined for a single sample. This query is constructed
in a straightforward manner, but it will result in us returning multiple copies
of an age if the sample is connected to more than one `geo_entity`. This is not
ideal, and we should consider either
1. Returning a list of `geo_entity` objects for each sample (this would be a more
   complex query), or
2. Limiting the data model so that only one `geo_entity` can be directly linked
   to a sample
*/
LEFT JOIN sample_geo_entity sg
  ON s.id = sg.sample_id
LEFT JOIN geo_entity g
  ON sg.geo_entity_id = g.id
WHERE location IS NOT NULL
  AND dt.unit = 'Ma' -- Poor proxy for age right now
  AND d.is_accepted
  AND NOT coalesce(d.is_bad, false);

CREATE VIEW core_view.sample_data AS
WITH a AS (
SELECT
	s.id,
	unnest(t.tree) material_id
FROM sample s
LEFT JOIN core_view.material_tree t
  ON s.material = t.id
),
b AS (
SELECT
  a.id,
  json_agg((SELECT m FROM (
    SELECT
    *
    FROM core_view.material
    WHERE id = a.material_id
  ) AS m)) material
FROM a
GROUP BY a.id
)
SELECT
  s.*,
  b.material material_data,
  is_public(s)
FROM sample s
LEFT JOIN b
  ON s.id = b.id;

/*
View to link projects with all member samples and sessions
*/
CREATE VIEW core_view.project_sample_session AS
SELECT
  p.id project_id,
  s.id sample_id,
  ss.id session_id
FROM session ss
LEFT JOIN sample s
  ON ss.sample_id = s.id
JOIN project p
  ON p.id = ss.project_id
UNION ALL
SELECT
  p.id,
  s.id sample_id,
  NULL
FROM sample s
JOIN project_sample ps
  ON ps.sample_id = s.id
JOIN project p
  ON p.id = ps.project_id;

CREATE VIEW core_view.project_extent AS
SELECT
  project_id,
  ST_Extent(location) extent,
  count(*) n
FROM core_view.project_sample_session p
JOIN sample s
  ON s.id = p.sample_id
WHERE location IS NOT null
GROUP BY p.project_id;

CREATE VIEW core_view.project AS
SELECT
	p.id,
	p.description,
	p.name,
  p.embargo_date,
  p.location_name,
  p.location_name_autoset,
  ST_AsGeoJSON(p.location)::jsonb geometry,
  NOT embargoed(p.embargo_date) AS is_public,
	-- Get data from researchers table in standard format
	to_jsonb((SELECT array_agg(a) FROM (
		SELECT r.* FROM researcher r
		JOIN project_researcher pr
		  ON pr.researcher_id = r.id
		WHERE pr.project_id = p.id
	) AS a)) AS researchers,
	-- Get data from publications table in standard format
	to_jsonb((SELECT array_agg(a) FROM (
		SELECT pub.* FROM publication pub
		  JOIN project_publication pp
		    ON pp.publication_id = pub.id
		 WHERE p.id = pp.project_id
	) AS a)) AS publications,
	-- Get data from samples table in standard format
	-- Note: we might convert this link to *analytical sessions*
	-- to cover cases when samples are in use by multiple projects
	to_jsonb((SELECT array_agg(a) FROM (
		SELECT DISTINCT ON (s.id)
      s.*
		FROM core_view.sample s
    JOIN session ss
      ON ss.sample_id = s.id
		WHERE ss.project_id = p.id
	) AS a)) AS samples
FROM project p
ORDER BY p.id;

COMMENT ON COLUMN core_view.project.samples IS
'Array of objects representing samples in the project
(each object follows the schema of "core_view.sample")';

/*
TODO: Oct 2020
This view is a shim for a foreign-keyed table that should be made available.
We currently have this on this `base_schema_change` branch but we
need to merge it in...
*/
DROP VIEW IF EXISTS vocabulary.authority;
CREATE VIEW vocabulary.authority AS
WITH a AS (
SELECT DISTINCT authority FROM vocabulary.analysis_type
UNION
SELECT DISTINCT authority FROM vocabulary.material
UNION
SELECT DISTINCT authority FROM vocabulary.entity_reference
UNION
SELECT DISTINCT authority FROM vocabulary.parameter
UNION
SELECT DISTINCT authority FROM vocabulary.material
UNION
SELECT DISTINCT authority FROM vocabulary.method
UNION
SELECT DISTINCT authority FROM vocabulary.unit
UNION
SELECT DISTINCT authority FROM vocabulary.error_metric
UNION
SELECT DISTINCT authority FROM vocabulary.analysis_type
UNION
SELECT DISTINCT authority FROM geo_entity
)
SELECT DISTINCT authority id FROM a
WHERE authority IS NOT null
ORDER BY authority;
