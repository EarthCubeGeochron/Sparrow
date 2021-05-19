/*
A procedure to run at initialization if the document tables are empty. 
*/

DO $$
BEGIN
IF (NOT EXISTS(SELECT FROM documents.project_document)) THEN
INSERT INTO documents.project_document(project_id,project_body,project_token)
SELECT
p.id,
(p.*, pub.*,res.*)::text,
to_tsvector((p.*, pub.*,res.*)::text)
FROM project p
LEFT JOIN project_publication pp
ON pp.project_id = p.id
LEFT JOIN publication pub
ON pp.publication_id = pub.id
LEFT JOIN project_researcher pr
ON pr.project_id = p.id
LEFT JOIN researcher res
ON pr.researcher_id=res.id;
END IF;


IF (NOT EXISTS(SELECT FROM documents.sample_document)) THEN
INSERT INTO documents.sample_document(sample_id, sample_body, sample_token)
SELECT
s.id,
(s.*,g.*)::text,
to_tsvector((s.*,g.*)::text)
FROM sample s
LEFT JOIN sample_geo_entity sge
ON sge.sample_id = s.id
LEFT JOIN geo_entity g
ON sge.geo_entity_id=g.id;
END IF;

IF (NOT EXISTS(SELECT FROM documents.session_document)) THEN
INSERT INTO documents.session_document(session_id,session_body,session_token)
SELECT
ss.id,
(ss.*,ins.*)::text,
to_tsvector((ss.*,ins.*)::text)
FROM session ss
LEFT JOIN instrument ins
ON ins.id = ss.instrument;
END IF;
END
$$
