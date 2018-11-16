-- Set up project--publication links
INSERT INTO project (id, title, description) VALUES
( 'zebra-nappe',
  'Zebra Nappe',
  'Structural study of the southernmost nappe of the Naukluft Nappe Complex, Namibia' ),
( 'crystal-knob',
  'Crystal Knob',
  'Mantle xenoliths from Crystal Knob, California');

INSERT INTO researcher (id, name, orcid) VALUES
( 'davenquinn', 'Daven P. Quinn', '0000-0003-1895-3742');

INSERT INTO publication (title, doi) VALUES
( 'Late Cretaceous construction of the mantle lithosphere beneath the central California coast revealed by Crystal Knob xenoliths',
  '10.1029/2017GC007260');

INSERT INTO project_researcher (project_id, researcher_id) VALUES
( 'crystal-knob', 'davenquinn');

INSERT INTO project_publication (project_id, publication_id)
SELECT 'crystal-knob', id
FROM publication
WHERE doi = '10.1029/2017GC007260';

-- Set up samples
INSERT INTO sample (id, project_id)
SELECT DISTINCT ON (sample)
  sample,
  'zebra-nappe'
FROM test_data.detrital_zircon;

-- Materials
INSERT INTO vocabulary.material (id, description, type_of)
VALUES
('rock', 'Rock', null),
('mineral','Mineral', null),
('xenolith', 'Xenolith', 'rock'),
('sp-xeno','Spinel peridotite xenolith', 'xenolith'),
('basalt', 'Basalt', 'rock'),
('pyx', 'Pyroxene', 'mineral'),
('cpx', 'Clinopyroxene', 'pyx'),
('opx', 'Orthopyroxene', 'pyx');

WITH s AS (
  SELECT sample_id FROM test_data.probe_session
  UNION ALL
  SELECT sample_id FROM test_data.sims_measurement
)
INSERT INTO sample (id, material, project_id)
SELECT DISTINCT ON (sample_id)
  sample_id,
  CASE WHEN sample_id = 'CK-2'
    THEN 'basalt'
    ELSE 'sp-xeno'
  END,
  'crystal-knob'
FROM s;

INSERT INTO instrument (name, description) VALUES
('IMS-7fGEO', 'SIMS for rock geochemical analysis'),
('Element2', 'LA-ICP mass spectrometer'),
('JEOL JXA-8200', 'Electron probe microanalyzer');

COMMIT;
/*
We'd have to go back to the raw data to recover the real
sessions, since our project-specific database doesn't include
this info.
*/
INSERT INTO session (sample_id, date, technique, instrument, target)
SELECT
	sample_id,
	'2013-06-05' date,
	'SIMS' technique,
	(SELECT id FROM instrument WHERE name = 'IMS-7fGEO') instrument,
  'sp-xeno'
FROM test_data.sims_measurement
GROUP BY (sample_id);

INSERT INTO vocabulary.unit (id, description)
VALUES
('ppm_chondrite', 'atomic ppm normalized to Workman and Hart chondrite abundances'),
('ppm (atomic)', 'atomic ppm (raw values)') -- Overlaps with EarthChem definition
ON CONFLICT DO NOTHING;

INSERT INTO vocabulary.error_metric (id, description)
VALUES
('std', 'Standard deviation')
ON CONFLICT DO NOTHING;

WITH a AS (
SELECT
	id orig_id,
	(SELECT id FROM session WHERE sample_id = s.sample_id) session_id,
	mineral,
	name
FROM test_data.sims_measurement s
),
b AS (
SELECT
orig_id,
session_id,
row_number() OVER(
	PARTITION BY session_id
	ORDER BY mineral, name
) session_index,
mineral material
FROM a
),
c AS (
INSERT INTO analysis (session_id, session_index, material)
SELECT session_id, session_index, material
FROM b
RETURNING id, session_id, session_index
),
index AS (
SELECT
	orig_id,
	c.session_id,
	c.session_index,
	id new_id
FROM c
JOIN b
  ON c.session_id = b.session_id
  AND c.session_index = b.session_index
),
__step5 AS (
SELECT
  new_id analysis_id,
  (SELECT symbol FROM vocabulary.element WHERE number = s.element) parameter,
  norm_ppm,
  norm_std,
  raw_ppm,
  raw_std,
  bad
FROM test_data.sims_datum s
JOIN index ON s.measurement_id = index.orig_id
),
-- All data
__all_data AS (
SELECT
analysis_id,
parameter,
norm_ppm datum,
norm_std error,
'ppm_chondrite' AS unit,
'norm' AS type,
true AS is_computed,
bad is_bad
FROM __step5
UNION ALL
SELECT
analysis_id,
parameter,
raw_ppm datum,
raw_std error,
'ppm (atomic)' AS unit,
'raw' AS type,
false AS is_computed,
bad is_bad
FROM __step5
),
__setup_parameters AS (
INSERT INTO vocabulary.parameter (id)
SELECT DISTINCT ON (parameter)
parameter
FROM __all_data
ON CONFLICT DO NOTHING
),
__insert_datum_type AS (
INSERT INTO datum_type (parameter, unit, error_unit, error_metric, is_computed, is_interpreted)
SELECT DISTINCT ON (parameter, type)
parameter,
unit,
unit error_unit,
'std',
is_computed,
false
FROM __all_data
ON CONFLICT (parameter, unit, error_unit, error_metric, is_computed, is_interpreted)
DO UPDATE SET is_computed = EXCLUDED.is_computed
RETURNING *
)
INSERT INTO datum (analysis, type, value, error, is_bad)
SELECT
	analysis_id,
	t.id,
	datum AS value,
	error,
	is_bad
FROM __all_data v
JOIN __insert_datum_type t
  ON t.parameter = v.parameter
 AND t.unit = v.unit
 AND t.error_unit = v.unit
ON CONFLICT DO NOTHING
RETURNING *;

DROP TABLE vocabulary.element;
