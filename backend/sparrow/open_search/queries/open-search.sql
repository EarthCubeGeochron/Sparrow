/*
Open search for getting all the models back at a time
*/
WITH search AS (
    SELECT to_tsquery(string_agg(lexeme || ':*', ' & ' order by positions)) AS query
    FROM unnest(to_tsvector(:query))
)
SELECT DISTINCT 'project' model, to_jsonb(p.*) json
FROM search, project p
LEFT JOIN documents.project_document pd
ON pd.project_id = p.id
LEFT JOIN project_sample ps 
ON ps.project_id = p.id
LEFT JOIN documents.sample_document sd
ON sd.sample_id = ps.sample_id
LEFT JOIN session ss
ON ss.project_id = p.id
LEFT JOIN documents.session_document ssd
ON ssd.session_id = ss.id
WHERE 
pd.project_token @@ search.query OR
sd.sample_token @@ search.query OR
ssd.session_token @@ search.query
UNION
SELECT DISTINCT 'sample' model, to_jsonb(t.*)
FROM (
SELECT DISTINCT s.id, s.name, s.material, location_name, ST_AsGeoJSON(s.location)::jsonb as location, s.elevation, s.embargo_date
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
ssd.session_token @@ search.query) t
UNION
SELECT DISTINCT 'session' model, to_jsonb(se.*)
FROM (
SELECT DISTINCT ss.id, ss.date, ss.date_precision, ss.end_date,ss.instrument, ss.technique, ss.target, ss.embargo_date, ss.data
FROM search, session ss
LEFT JOIN documents.session_document ssd
ON ssd.session_id=ss.id
LEFT JOIN documents.project_document pd 
ON pd.project_id = ss.project_id
LEFT JOIN documents.sample_document sd
ON sd.sample_id = ss.sample_id
WHERE 
sd.sample_token @@ search.query OR
pd.project_token @@ search.query OR
ssd.session_token @@ search.query) se
;