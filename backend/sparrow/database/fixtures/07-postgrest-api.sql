
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
      -- Snapping to a grid allows us to group nearby points together
      ST_SnapToGrid(ST_AsMVTGeom(geometry, (SELECT envelope FROM tile_loc)), 4, 4) geometry
    FROM tile_features
  ),
  grouped_features AS (
    SELECT
      geometry,
      count(*) n,
      CASE WHEN count(*) < 10 THEN
        array_agg(id)
      ELSE
        null
      END id,
      CASE WHEN count(*) < 10 THEN
        array_agg(name)
      ELSE
        null
      END AS name,
      CASE WHEN count(*) < 10 THEN
        array_agg(material)
      ELSE
        null
      END material
    FROM mvt_features
    GROUP BY geometry
  )
  SELECT ST_AsMVT(grouped_features)
  FROM grouped_features;
$$ LANGUAGE sql IMMUTABLE;