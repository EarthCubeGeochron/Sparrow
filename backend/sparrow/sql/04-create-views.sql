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

/*
A session view with some extra features
*/
CREATE VIEW core_view.session AS
SELECT
	s.*,
	i.name instrument_name,
  p.title project_name,
  is_public(s)
FROM session s
LEFT JOIN instrument i
  ON i.id = s.instrument
LEFT JOIN project p
  ON s.project_id = p.id
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
  ( SELECT
      name
    FROM instrument
    WHERE id = s.instrument
  ) instrument,
  sa.id sample_id,
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
  sa.igsn,
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
  is_public(s),
  a.session_id,
  a.session_index,
  s.sample_id,
  s.technique
FROM datum d
JOIN analysis a
  ON d.analysis = a.id
JOIN datum_type t
  ON d.type = t.id
JOIN session s
  ON a.session_id = s.id
ORDER BY d.id;

CREATE VIEW core_view.age_datum AS
SELECT *
FROM core_view.datum
WHERE unit IN ('Ga','Ma');

CREATE VIEW core_view.material AS
SELECT id, description, authority
FROM vocabulary.material;

CREATE VIEW core_view.sample AS
SELECT
  s.id,
  s.igsn,
  s.material,
  ST_AsGeoJSON(s.location) geometry,
  location_name,
  location_precision,
  p.id project_id,
  p.title project_title,
  is_public(s)
FROM sample s
JOIN session ss
  ON s.id = ss.sample_id
LEFT JOIN project p
  ON ss.project_id = p.id;

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

CREATE VIEW core_view.project AS
SELECT
	p.id,
	p.description,
	p.title,
  p.embargo_date,
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
		SELECT DISTINCT ON (s.id) *
		FROM core_view.sample s
    JOIN session ss
      ON ss.sample_id = s.id
		WHERE ss.project_id = p.id
	) AS a)) AS samples
FROM project p;

COMMENT ON COLUMN core_view.project.samples IS
'Array of objects representing samples in the project
(each object follows the schema of "core_view.sample")';
