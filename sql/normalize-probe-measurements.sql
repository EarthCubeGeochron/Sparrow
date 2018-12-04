/*
We'd have to go back to the raw data to recover the real
sessions, since our project-specific database doesn't include
this info.
*/

INSERT INTO vocabulary.error_metric (id, description)
VALUES ('percent', 'Percent') ON CONFLICT DO NOTHING;

INSERT INTO vocabulary.material (id, description, type_of)
VALUES ('sp', 'Spinel', 'mineral'),
	   ('ol', 'Olivine', 'mineral')
ON CONFLICT DO NOTHING;

INSERT INTO vocabulary.parameter (id, description)
VALUES
('Mg#', 'Molar Mg2O3/(Mg+FeO)*100 - calculated assuming all iron is reduced'),
('Cr#', 'Molar Cr2O3/(Cr2O3+Al2O3)*100')
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

WITH measurement_data AS (
SELECT
	s.id session_id,
	ps.sample_id,
	m.line_number AS session_index,
	m.session_id old_session_id,
	cr_number,
	mg_number,
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
 AND s.technique = 'EMP'
 )
INSERT INTO analysis (session_id, session_index, material)
SELECT session_id, session_index, material
FROM measurement_data
ON CONFLICT (session_id, session_index) DO NOTHING;

