/* Manually updating location data from Schaen, et al. */
-- 1. Created table Schaen Table 2 from cleaned paper table

-- 2. Updated rock types in `vocabulary.material`

-- 3.
INSERT INTO vocabulary.material (id)
SELECT DISTINCT rock_type FROM method_data.schaen_table_2
ON CONFLICT DO NOTHING;

UPDATE sample SET
  location = ST_SetSRID(ST_MakePoint(lon,lat),4326),
  location_precision = 0,
  material = rock_type,
  location_name = island || ' Island'
FROM method_data.schaen_table_2
WHERE sample_id = name;

-- 4. Named project 'delarof-1', Delarof Islands Magmatic Evolution

-- 5. Linked publication
-- 'Eocene to Pleistocene magmatic evolution of the Delarof Islands, Aleutian Arc' Schaen 10.1002/2015GC006067

-- 6.
UPDATE session SET
  project_id = 1
WHERE sample_id IN (
  SELECT id
  FROM sample s
  JOIN method_data.schaen_table_2
  ON sample_id = s.name);

/*
Importing Cretaceous data
*/

UPDATE sample SET
  location = ST_SetSRID(ST_MakePoint(-106.9123,41.6032),4326),
  location_precision = 50000,
  material = 'bentonite',
  location_name = 'Carbon County, WY'
WHERE name = 'D2315';

/* Projects and samples are linked through the analytical sessions,
   so update those */
UPDATE session
SET project_id = 2
WHERE sample_id = (SELECT id FROM sample WHERE name = 'D2315');
