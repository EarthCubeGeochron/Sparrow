/*
A sql query that uses tsvectors and tsqueries to perform a fuzzy search
on table rows that are converted to tsvectors
*/

WITH search AS (
    SELECT to_tsquery(string_agg(lexeme || ':*', ' & ' order by positions)) AS query
    FROM unnest(to_tsvector(:query))
)
SELECT p.*
FROM search, project p
LEFT JOIN project_sample ps 
ON ps.project_id = p.id
LEFT JOIN sample s
ON s.id = ps.sample_id
LEFT JOIN session ss
ON ss.sample_id = s.id
LEFT JOIN project_publication pp
ON pp.project_id = p.id
LEFT JOIN publication pu
ON pu.id = pp.publication_id
WHERE to_tsvector(p::text) @@ search.query OR
to_tsvector(s::text) @@ search.query OR
to_tsvector(ss::text) @@ search.query OR
to_tsvector(pu::text) @@ search.query;