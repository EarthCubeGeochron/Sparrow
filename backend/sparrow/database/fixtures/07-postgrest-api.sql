-- API-specific roles
-- https://postgrest.org/en/stable/tutorials/tut0.html
CREATE ROLE authenticator LOGIN NOINHERIT NOCREATEDB NOCREATEROLE NOSUPERUSER;

GRANT admin TO authenticator;
GRANT view_public TO authenticator;

CREATE SCHEMA IF NOT EXISTS sparrow_api;

CREATE OR REPLACE VIEW sparrow_api.analysis AS
SELECT * FROM core_view.analysis;

CREATE OR REPLACE VIEW sparrow_api.datum AS
SELECT * FROM core_view.datum;

CREATE OR REPLACE VIEW sparrow_api.attribute AS
SELECT * FROM core_view.attribute;

CREATE OR REPLACE VIEW sparrow_api.project AS
SELECT * FROM core_view.project;

CREATE OR REPLACE VIEW sparrow_api.session AS
SELECT * FROM core_view.session;

CREATE OR REPLACE VIEW sparrow_api.sample AS
SELECT * FROM sample;

CREATE OR REPLACE VIEW sparrow_api.sample_data AS
SELECT * FROM core_view.sample;

CREATE OR REPLACE VIEW core_view.sample_v3 AS
SELECT
  s.id,
  s.igsn,
  s.name,
  s.material,
  s.location geometry,
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

/* A function to create vector tiles that doesn't require a separate tile server.
  This could be upgraded to pg_tileserv eventually.
 */
CREATE OR REPLACE FUNCTION sparrow_api.sample_tile(
  x integer,
  y integer,
  z integer
) RETURNS bytea AS $$
  WITH tile_loc AS (
    SELECT tile_utils.envelope(x, y, z) envelope 
  ),
  -- features in tile envelope
  tile_features AS (
    SELECT
      id,
      name,
      material,
      ST_Transform(geometry, 3857) geometry
    FROM core_view.sample_v3
    WHERE ST_Intersects(geometry, ST_Transform((SELECT envelope FROM tile_loc), 4326))
  ),
  mvt_features AS (
    SELECT
      id,
      name,
      material,
      -- Get the geometry in vector-tile integer coordinates
      ST_AsMVTGeom(geometry, (SELECT envelope FROM tile_loc)) geometry
    FROM tile_features
  ),
  snapped_features AS (
    SELECT
      id,
      name,
      material,
      geometry,
      -- Snapping to a grid allows us to efficiently group nearby points together
      -- We could also use the ST_ClusterDBSCAN function for a less naive implementation
      ST_SnapToGrid(geometry, 8, 8) snapped_geometry
      --ST_ClusterDBSCAN(geometry, 16, 2) OVER () cluster_id
    FROM mvt_features
  ),
  grouped_features AS (
    SELECT
      -- Get cluster expansion zoom level
      tile_utils.cluster_expansion_zoom(ST_Collect(geometry), z) expansion_zoom,
      snapped_geometry geometry,
      count(*) n,
      CASE WHEN count(*) < 10 THEN
        string_agg(id::text, ',')
      ELSE
        null
      END id,
      CASE WHEN count(*) < 10 THEN
        string_agg(replace(name, ',', ';'), ',')
      ELSE
        null
      END AS name,
      CASE WHEN count(*) < 10 THEN
        string_agg(material, ',')
      ELSE
        null
      END material
    FROM snapped_features
    GROUP BY snapped_geometry
    -- WHERE cluster_id IS NOT NULL
    -- GROUP BY cluster_id
    -- UNION ALL
    -- SELECT
    --   null,
    --   geometry,
    --   1 n,
    --   id::text,
    --   name,
    --   material
    -- FROM snapped_features
    --WHERE cluster_id IS NULL
  )
  SELECT ST_AsMVT(grouped_features)
  FROM grouped_features;
$$ LANGUAGE sql IMMUTABLE;


/* Supporting records and vocabularies */
CREATE OR REPLACE VIEW sparrow_api.researcher AS
SELECT * FROM researcher;

CREATE OR REPLACE VIEW sparrow_api.publication AS
SELECT * FROM publication;

CREATE OR REPLACE VIEW sparrow_api.instrument AS
SELECT * FROM instrument;

CREATE OR REPLACE VIEW sparrow_api.datum_type AS
SELECT * FROM datum_type;

CREATE OR REPLACE VIEW sparrow_api.material AS
SELECT * FROM vocabulary.material;

CREATE OR REPLACE VIEW sparrow_api.method AS
SELECT * FROM vocabulary.method;

CREATE OR REPLACE VIEW sparrow_api.parameter AS
SELECT * FROM vocabulary.parameter;

CREATE OR REPLACE VIEW sparrow_api.unit AS
SELECT * FROM vocabulary.unit;

CREATE OR REPLACE VIEW sparrow_api.error_metric AS
SELECT * FROM vocabulary.error_metric;

CREATE OR REPLACE VIEW sparrow_api.analysis_type AS
SELECT * FROM vocabulary.analysis_type;

CREATE OR REPLACE VIEW sparrow_api.authority AS
SELECT * FROM vocabulary.authority;

CREATE OR REPLACE VIEW sparrow_api.age_context AS
SELECT * FROM core_view.age_context;

/* Data files, and what was loaded from each */
CREATE OR REPLACE VIEW sparrow_api.data_file AS
SELECT * FROM data_file;

CREATE OR REPLACE VIEW sparrow_api.data_file_link AS
SELECT * FROM data_file_link;

/* Counts describing the lab's holdings */
CREATE OR REPLACE VIEW sparrow_api.metrics AS
WITH
d AS (SELECT count(DISTINCT project.id) number_of_projects FROM core_view.project),
c AS (SELECT count(DISTINCT sample.name) number_of_samples FROM core_view.sample),
e AS (SELECT count(DISTINCT session.id) number_of_sessions FROM core_view.session),
f AS (SELECT count(DISTINCT analysis_id) number_of_analyses FROM core_view.analysis),
g AS (SELECT count(DISTINCT datum_id) number_of_datum FROM core_view.datum),
b AS (SELECT count(DISTINCT sample.material) number_of_materials FROM core_view.sample WHERE sample.material IS NOT NULL),
a AS (SELECT count(DISTINCT s.name) samples_with_location FROM core_view.sample s WHERE s.geometry IS NOT NULL),
j AS (SELECT array_agg(DISTINCT a.technique) techniques FROM core_view.age_datum a),
k AS (SELECT array_agg(DISTINCT a.target) targets FROM core_view.age_context a),
l AS (SELECT count(DISTINCT a.geo_entity_name) number_of_formations_connected FROM core_view.age_context a)
SELECT * FROM a, b, c, d, e, f, g, j, k, l;

GRANT USAGE ON SCHEMA sparrow_api TO view_public;
GRANT SELECT ON ALL TABLES IN SCHEMA sparrow_api TO view_public;
GRANT USAGE ON SCHEMA sparrow_api TO admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA sparrow_api TO admin;

-- Administrators add records through the API, which draws on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO admin;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA vocabulary TO admin;

-- Where a lab keeps its files is not for the public
REVOKE ALL ON sparrow_api.data_file, sparrow_api.data_file_link FROM view_public;


NOTIFY pgrst, 'reload schema'