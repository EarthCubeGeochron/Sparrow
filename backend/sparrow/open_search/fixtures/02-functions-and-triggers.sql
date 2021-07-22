/*
Trigger functions to make sure we're updating document when NEW data gets entered
*/

CREATE OR REPLACE FUNCTION project_doc_insert(project_id_ int)
	RETURNS BOOLEAN AS
$$
BEGIN
	IF project_id_ IS NULL THEN
		RAISE EXCEPTION 'project id is null';
		
		RETURN FALSE;
	END IF;
	
	INSERT INTO documents.project_document(project_id, project_body, project_token)
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
	ON pr.researcher_id=res.id
	WHERE p.id = project_id_;
	
	RETURN TRUE;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION project_doc_update() 
	RETURNS TRIGGER 
	AS
$$
DECLARE success BOOLEAN;
BEGIN
	success = project_doc_insert(NEW.id);
	
	IF success IS FALSE THEN
		RAISE EXCEPTION 'Did not insert successfully';
	END IF;
	
	
	RETURN NEW;
END;
$$
LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS project_doc ON project;
CREATE TRIGGER project_doc
	AFTER INSERT OR UPDATE ON project
	FOR EACH ROW
	EXECUTE PROCEDURE project_doc_update();

CREATE OR REPLACE FUNCTION sample_doc_insert(sample_id_ int)
	RETURNS BOOLEAN AS
$$
BEGIN

	IF sample_id_ IS NULL THEN
		RAISE EXCEPTION 'sample id is null';
		
		RETURN FALSE;
	END IF;

	INSERT INTO documents.sample_document(sample_id, sample_body, sample_token)
	SELECT
	s.id,
	(s.*,g.*)::text,
	to_tsvector((s.*,g.*)::text)
	FROM sample s
	LEFT JOIN sample_geo_entity sge
	ON sge.sample_id = s.id
	LEFT JOIN geo_entity g
	ON sge.geo_entity_id=g.id
	WHERE s.id = sample_id_;
		
	RETURN TRUE;

END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sample_doc_update() 
	RETURNS TRIGGER 
	AS
$$
DECLARE success BOOLEAN;
BEGIN
	success = sample_doc_insert(NEW.id);
	
	IF success IS FALSE THEN
		RAISE EXCEPTION 'Did not insert successfully';
	END IF;
	
	RETURN NEW;

END;
$$
LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS sample_doc ON sample;
CREATE TRIGGER sample_doc
	AFTER INSERT OR UPDATE ON sample
	FOR EACH ROW
	EXECUTE PROCEDURE sample_doc_update();

CREATE OR REPLACE FUNCTION session_doc_insert(session_id_ int)
	RETURNS BOOLEAN AS
$$
BEGIN
	IF session_id_ IS NULL THEN
		RAISE EXCEPTION 'session id is null';
		
		RETURN FALSE;
	END IF;

	INSERT INTO documents.session_document(session_id,session_body,session_token)
	SELECT
	ss.id,
	(ss.*,ins.*)::text,
	to_tsvector((ss.*,ins.*)::text)
	FROM session ss
	LEFT JOIN instrument ins
	ON ins.id = ss.instrument
	WHERE ss.id = session_id_;

	RETURN TRUE;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION session_doc_update() 
	RETURNS TRIGGER 
	AS
$$
DECLARE success BOOLEAN;
BEGIN
	success = session_doc_insert(NEW.id);
	
	IF success IS FALSE THEN
		RAISE EXCEPTION 'Did not insert successfully';
	END IF;

	RETURN NEW;
END;
$$
LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS session_doc ON session;
CREATE TRIGGER session_doc
	AFTER INSERT OR UPDATE ON session
	FOR EACH ROW
	EXECUTE PROCEDURE session_doc_update();


