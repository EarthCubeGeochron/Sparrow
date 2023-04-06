/*
A sql query that uses tsvectors and tsqueries to perform a fuzzy search
on table rows that are converted to tsvectors
*/

WITH search AS (
    SELECT to_tsquery(string_agg(lexeme || ':*', ' & ' order by positions)) AS query
    FROM unnest(to_tsvector(:query))
)
SELECT DISTINCT p.*
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
ssd.session_token @@ search.query;