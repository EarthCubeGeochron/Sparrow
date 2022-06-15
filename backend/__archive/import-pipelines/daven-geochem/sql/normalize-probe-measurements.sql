/*
We'd have to go back to the raw data to recover the real
sessions, since our project-specific database doesn't include
this info.
*/

INSERT INTO vocabulary.error_metric (id, description)
-- percent symbols are escaped with %%
VALUES ('%%', 'Percent') ON CONFLICT DO NOTHING;

INSERT INTO vocabulary.material (id, description, type_of)
VALUES ('sp', 'Spinel', 'mineral'),
	   ('ol', 'Olivine', 'mineral')
ON CONFLICT DO NOTHING;

INSERT INTO vocabulary.parameter (id, description)
VALUES
('Mg#', 'Molar Mg2O3/(Mg+FeO)*100 - calculated assuming all iron is reduced'),
('Cr#', 'Molar Cr2O3/(Cr2O3+Al2O3)*100'),
('oxide_total', 'Total of all oxides measured for a microprobe spot')
ON CONFLICT DO NOTHING;

/*
Insert session data
*/
INSERT INTO session (sample_id, date, instrument, technique)
SELECT
  sample_id,
  date,
  (SELECT id FROM instrument WHERE name='JEOL JXA-8200') AS instrument,
  'EMP' AS technique
FROM test_data.probe_session
ON CONFLICT DO NOTHING;

INSERT INTO datum_type
(parameter, unit, error_metric, is_computed, is_interpreted, description)
VALUES
('Mg#', '%%', '%%', true, true, 'Microprobe-measured Mg# (computed from modeled stoichiometry)'),
('Cr#', '%%', '%%', true, true, 'Microprobe-measured Cr# (computed from modeled stoichiometry)'),
('oxide_total', 'wt%%', '%%', true, false, 'Microprobe-measured oxide total');

INSERT INTO datum_type
(parameter, unit, error_metric, is_computed, is_interpreted)
SELECT DISTINCT ON (oxide)
oxide, 'wt%%', '%%', false, false
FROM test_data.probe_datum
UNION ALL
SELECT DISTINCT ON (oxide)
oxide, 'mol%%', '%%', false, false
FROM test_data.probe_datum;

COMMIT;

CREATE SCHEMA temporary;

/* Temporary table to store measurement values */
CREATE TABLE temporary.measurement_data AS
SELECT
	s.id session_id,
	ps.sample_id,
  m.id old_measurement_id,
	m.line_number AS session_index,
	m.session_id old_session_id,
	cr_number,
	mg_number,
  oxide_total,
	location,
	CASE WHEN m.mineral = 'na'
    THEN null
	  ELSE m.mineral
  END material
FROM test_data.probe_measurement m
JOIN test_data.probe_session ps
  ON ps.id = m.session_id
JOIN session s
  ON ps.sample_id = s.sample_id
 AND ps.date = s.date
 AND s.instrument = (SELECT id FROM instrument WHERE name='JEOL JXA-8200')
 AND s.technique = 'EMP';

INSERT INTO analysis (session_id, session_index, material)
SELECT session_id, session_index, material
FROM temporary.measurement_data
ON CONFLICT DO NOTHING;

CREATE TABLE temporary.measurement_link AS
SELECT
  a.id analysis,
  m.*
FROM temporary.measurement_data m
JOIN analysis a
  ON a.session_id = m.session_id
 AND a.session_index = m.session_index;

/* Insert derived/secondary datum types */
INSERT INTO datum (analysis, type, value)
SELECT
  analysis,
  (SELECT id FROM datum_type WHERE parameter = 'Mg#'),
  mg_number
FROM temporary.measurement_link
WHERE mg_number IS NOT NULL
UNION ALL
SELECT
  analysis,
  (SELECT id FROM datum_type WHERE parameter = 'Cr#'),
  cr_number
FROM temporary.measurement_link
WHERE cr_number IS NOT NULL
UNION ALL
SELECT
  analysis,
  (SELECT id FROM datum_type WHERE parameter = 'oxide_total'),
  oxide_total
FROM temporary.measurement_link
WHERE oxide_total IS NOT NULL;

/* Insert basic oxide and computed molar data */
INSERT INTO datum (analysis, type, value, error)
SELECT
  m.analysis,
  (SELECT id FROM datum_type WHERE parameter = d.oxide AND unit = 'wt%%') AS type,
  d.weight_percent AS value,
  d.error
FROM test_data.probe_datum d
JOIN temporary.measurement_link m
  ON m.old_measurement_id = d.measurement_id
UNION ALL
SELECT
  m.analysis,
  (SELECT id FROM datum_type WHERE parameter = d.oxide AND unit = 'mol%%') AS type,
  d.molar_percent AS value,
  d.error
FROM test_data.probe_datum d
JOIN temporary.measurement_link m
  ON m.old_measurement_id = d.measurement_id;

DROP SCHEMA temporary CASCADE;

