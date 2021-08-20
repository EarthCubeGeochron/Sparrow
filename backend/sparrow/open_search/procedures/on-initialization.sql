/*
A procedure to run at initialization if the document tables are empty. 
*/

DO $$
BEGIN
IF (NOT EXISTS(SELECT FROM documents.project_document)) THEN
    SELECT project_doc_insert(p.id) FROM project p;
END IF;


IF (NOT EXISTS(SELECT FROM documents.sample_document)) THEN
    SELECT sample_doc_insert(s.id) FROM sample s;
END IF;

IF (NOT EXISTS(SELECT FROM documents.session_document)) THEN
    SELECT session_doc_insert(ss.id) FROM session ss;
END IF;
END
$$
