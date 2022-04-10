/*
Open search for the Session model
*/
WITH search AS (
    SELECT to_tsquery(string_agg(lexeme || ':*', ' & ' order by positions)) AS query
    FROM unnest(to_tsvector(:query))
)
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
ssd.session_token @@ search.query;