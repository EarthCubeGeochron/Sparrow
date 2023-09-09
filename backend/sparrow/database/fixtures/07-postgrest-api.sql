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


GRANT USAGE ON SCHEMA sparrow_api TO view_public;
GRANT SELECT ON ALL TABLES IN SCHEMA sparrow_api TO view_public;
GRANT USAGE ON SCHEMA sparrow_api TO admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA sparrow_api TO admin;


NOTIFY pgrst, 'reload schema'