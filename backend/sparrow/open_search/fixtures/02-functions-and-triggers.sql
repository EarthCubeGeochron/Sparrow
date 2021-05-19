/*
Trigger functions to make sure we're updating document when new data gets entered
*/

CREATE OR REPLACE FUNCTION project_doc_update() 
	RETURNS TRIGGER AS
$BODY$
BEGIN
	-- what should be included here.. publication, researcher
    INSERT INTO documents.project_document(project_id, project_body, project_token)
    SELECT 
	new.id,
	(new.*,pub.*, res.*)::text,
	to_tsvector((pub.*, res.*)::text) 
	FROM publication pub 
	LEFT JOIN project_publication pp
	ON pp.publication_id = pub.id
	LEFT JOIN project_researcher pr 
	ON pr.project_id = new.id
	LEFT JOIN researcher res
	ON pr.researcher_id = res.id
	WHERE pr.project_id = new.id AND pp.project_id = new.id;

	RETURN new;

END;
$BODY$
language plpgsql;

DROP TRIGGER IF EXISTS project_doc ON project;
CREATE TRIGGER project_doc
	AFTER INSERT ON project
	FOR EACH ROW
	EXECUTE PROCEDURE project_doc_update();


CREATE OR REPLACE FUNCTION sample_doc_update() 
	RETURNS TRIGGER AS
$BODY$
BEGIN

	INSERT INTO documents.sample_document(sample_id, sample_body, sample_token)
	SELECT new.id,
	(new.*,g.*)::text,
	to_tsvector((new.*,g.*)::text)
	FROM geo_entity g
	LEFT JOIN sample_geo_entity sge
	ON sge.geo_entity_id = g.id
	WHERE sge.sample_id = new.id
	;

	RETURN new;

END;
$BODY$
language plpgsql;

DROP TRIGGER IF EXISTS sample_doc ON sample;
CREATE TRIGGER sample_doc
	AFTER INSERT ON sample
	FOR EACH ROW
	EXECUTE PROCEDURE sample_doc_update();


CREATE OR REPLACE FUNCTION session_doc_update() 
	RETURNS TRIGGER AS
$BODY$
BEGIN
	INSERT INTO documents.session_document(session_id, session_body, session_token)
	SELECT 
	new.id,
	(new.*,ins.*)::text,
	to_tsvector((new.*,ins.*)::text)
	FROM instrument ins
	LEFT JOIN session ss
	ON ss.instrument = ins.id
	WHERE ss.id = new.id;

	RETURN new;
END;
$BODY$
language plpgsql;

DROP TRIGGER IF EXISTS session_doc ON session;
CREATE TRIGGER session_doc
	AFTER INSERT ON session
	FOR EACH ROW
	EXECUTE PROCEDURE session_doc_update();


