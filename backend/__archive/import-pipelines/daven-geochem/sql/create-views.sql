/*
Create method-specific views
*/

CREATE VIEW method_data.dz_sample AS
WITH g AS (
SELECT
	s.sample_id,
	s.instrument,
	s.date,
	json_agg((SELECT z FROM (
	SELECT concordia,
	best_age,
	best_age_err AS err,
	best_age_system AS system,
	uranium_ppm,
	"ratio_U_Th",
	analysis_id) AS z)) AS grain_data
FROM method_data.detrital_zircon_analysis dz
JOIN analysis a ON a.id = dz.analysis_id
JOIN session s
  ON a.session_id = s.id
WHERE NOT a.is_standard -- Should replace with a link to standard sample id
GROUP BY (s.sample_id, s.instrument, s.date)
)
SELECT
	sample_id,
	(SELECT name FROM instrument WHERE id = instrument) instrument,
	"date",
	'2020-01-01'::timestamptz embargo_date,
	grain_data
FROM g;
