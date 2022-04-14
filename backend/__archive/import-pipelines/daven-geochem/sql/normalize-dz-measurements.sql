/*
We are trying something new here, since we only want to get age data into
the final API.

A typical detrital zircon measurement session consists of
100-1000 individual analyses, each of which has >10 data points:
isotope ratios, concordia figures, raw and interpreted best ages.
There could easily be 5-10 *thousand* rows added to the `datum` table
for a single sample.

Rather than fully normalizing DZ data, we take a different tack than we
use for SIMS and microprobe data -- we create a denormalized table
that is the main data store, and copy only *some* of the data into the
normalized datum/analysis store.

The denormalized table becomes a replacement for the entity-specific
MATERIALIZED VIEW that would be calculated for normalized data.

This approach saves us from creating large numbers of rows for related
datatypes in the `datum` table.
*/

INSERT INTO project (id, title, description) VALUES
( 'zebra-nappe',
  'Zebra Nappe',
  'Structural study of the southernmost nappe of the Naukluft Nappe Complex, Namibia' );

INSERT INTO vocabulary.method (id, description)
VALUES ('DZ-U/Pb', 'Detrital zircon U-Pb age determination')
ON CONFLICT DO NOTHING;

INSERT INTO vocabulary.material (id, description, type_of)
VALUES
('zircon', 'Zircon crystal', 'mineral'),
('zircon-standard', 'Zircon crystal from a laboratory standard', 'zircon'),
('sandstone', 'Sandstone', 'rock'),
('zircon-separate', 'Detrital zircon crystals mechanically separated from a rock', 'rock')
ON CONFLICT DO NOTHING;

-- Set up samples
INSERT INTO sample (id, project_id, material)
SELECT DISTINCT ON (sample)
  sample,
  'zebra-nappe',
  'sandstone'
FROM test_data.detrital_zircon;

INSERT INTO instrument (name, description) VALUES
('Element2', 'LA-ICP mass spectrometer at University of Arizona');

COMMIT;

INSERT INTO session (sample_id, date, instrument, technique, target)
SELECT DISTINCT ON (sample)
sample,
-- Guesstimated these dates
CASE WHEN sample IN ('SR-1','J-302','J-89','F-90')
  THEN '2017-06-30'::date
  ELSE '2018-08-30'::date
END,
(SELECT id FROM instrument WHERE name = 'Element2'),
'DZ-U/Pb',
'zircon-separate'
FROM test_data.detrital_zircon;

COMMIT;

INSERT INTO analysis (session_id, session_index, material, is_standard)
SELECT DISTINCT ON (sample, index)
  -- We can take this shortcut because we have only one session per sample
  (SELECT id FROM session WHERE sample_id = d.sample),
  index,
  CASE WHEN d.type = 'standard'
    THEN 'zircon-standard'
    ELSE 'zircon'
  END,
  type = 'standard'
FROM test_data.detrital_zircon d;

COMMIT;

CREATE SCHEMA IF NOT EXISTS method_data;

DROP TABLE IF EXISTS method_data.detrital_zircon_analysis;
CREATE TABLE method_data.detrital_zircon_analysis AS
SELECT DISTINCT ON (sample, index)
  (
  	SELECT id FROM analysis a
  	WHERE a.session_id=(SELECT id FROM session WHERE sample_id=d.sample)
    AND d.index = a.session_index
  ) analysis_id,
  uranium_ppm,
  "ratio_206Pb_204Pb",
  "ratio_U_Th",
  "ratio_206Pb_207Pb",
  "ratio_206Pb_207Pb_err",
  "ratio_207Pb_235U",
  "ratio_207Pb_235U_err",
  "ratio_206Pb_238U",
  "ratio_206Pb_238U_err",
  "error_corr",
  "age_206Pb_238U",
  "age_206Pb_238U_err",
  "age_207Pb_235U",
  "age_207Pb_235U_err",
  "age_206Pb_207Pb",
  "age_206Pb_207Pb_err",
  best_age,
  best_age_err,
  concordia,
  CASE
	WHEN best_age = "age_206Pb_238U" THEN '206Pb_238U'
	WHEN best_age = "age_207Pb_235U" THEN '207Pb_235U'
	WHEN best_age = "age_206Pb_207Pb" THEN '206Pb_207Pb'
	ELSE null
	END AS best_age_system
FROM test_data.detrital_zircon d;

ALTER TABLE method_data.detrital_zircon_analysis
  ADD PRIMARY KEY (analysis_id),
  ADD FOREIGN KEY (analysis_id) REFERENCES analysis(id);

/* Now that we've created a normalized "wide table" representation
   of detrital-zircon data, we can put *some* of the data in
   the datum table -- at the moment, we're interested in the
   interpreted "best age" for each analysis.
*/
INSERT INTO vocabulary.parameter (id, description)
VALUES
('age_206Pb_238U', 'Age for 206Pb-238U system'),
('age_207Pb_235U', 'Age for 207Pb-235U system'),
('age_206Pb_207Pb', 'Age for 206Pb-207Pb system'),
('U-Pb-best-age', 'Best age across U-Pb systems');

INSERT INTO datum_type (parameter, unit, error_metric, is_computed, is_interpreted)
VALUES
('U-Pb-best-age', 'Ma', 'std', true, true);

INSERT INTO datum (analysis, type, value, error)
SELECT
  analysis_id,
  (SELECT id FROM datum_type WHERE parameter='U-Pb-best-age'),
  best_age,
  best_age_err
FROM method_data.detrital_zircon_analysis;
