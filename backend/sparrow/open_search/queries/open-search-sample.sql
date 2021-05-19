/*
Like open search for project but for Samples
*/

WITH search AS (
    SELECT to_tsquery(string_agg(lexeme || ':*', ' & ' order by positions)) AS query
    FROM unnest(to_tsvector(:query))
)
SELECT DISTINCT s.id, s.name, s.material, location_name, ST_AsGEOJSON(s.location) as location, s.elevation, s.embargo_date
FROM search, sample s
LEFT JOIN documents.sample_document sd
ON sd.sample_id=s.id
LEFT JOIN project_sample ps 
ON ps.sample_id = s.id
LEFT JOIN documents.project_document p
ON p.project_id = ps.project_id
LEFT JOIN session ss
ON ss.sample_id = s.id
LEFT JOIN documents.session_document ssd
ON ssd.session_id=ss.id
WHERE 
sd.sample_token @@ search.query OR
p.project_token @@ search.query OR
ssd.session_token @@ search.query;
