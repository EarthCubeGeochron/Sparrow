WITH A AS(
SELECT
  s.id,
  s.name,
  s.material,
  ST_AsGeoJSON(s.location)::jsonb geometry,
  p.id project_id,
  p.name project_name,
  pub.id publication_id,
  pub.doi doi
FROM sample s
LEFT JOIN session ss
  ON s.id = ss.sample_id
LEFT JOIN project p
  ON ss.project_id = p.id
LEFT JOIN project_publication proj_pub
  on p.id = proj_pub.project_id
LEFT JOIN publication pub
  ON proj_pub.publication_id = pub.id
ORDER BY s.id)
  SELECT DISTINCT * 
  FROM A
  ORDER BY A.id;