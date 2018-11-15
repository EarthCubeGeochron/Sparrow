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

WITH s AS (
  SELECT sample_id FROM test_data.probe_session
  UNION ALL
  SELECT sample_id FROM test_data.sims_measurement
)
INSERT INTO sample (id, project_id)
SELECT DISTINCT ON (sample_id)
  sample_id,
  'crystal-knob'
FROM s;

INSERT INTO instrument (name, description) VALUES
("IMS-7fGEO", "SIMS for rock geochemical analysis"),
("Element2", "LA-ICP mass spectrometer"),
("JEOL JXA-8200", "Electron probe microanalyzer");
