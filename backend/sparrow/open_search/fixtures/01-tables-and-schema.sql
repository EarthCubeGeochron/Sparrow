/*
Creates the documents schema and associated tables, tsvector column is queriable

Also adds GIN indexing to speed up query, especially multiword queries
*/

CREATE SCHEMA IF NOT EXISTS documents;

CREATE TABLE IF NOT EXISTS documents.project_document(
    id serial PRIMARY KEY,
    project_id integer REFERENCES project(id) ON DELETE CASCADE,
    project_body text,
    project_token tsvector
);

CREATE INDEX IF NOT EXISTS project_document_gin ON documents.project_document USING GIN(project_token);

CREATE TABLE IF NOT EXISTS documents.sample_document(
    id serial PRIMARY KEY,
    sample_id integer REFERENCES sample(id) ON DELETE CASCADE,
    sample_body text,
    sample_token tsvector
);

CREATE INDEX IF NOT EXISTS sample_document_gin ON documents.sample_document USING GIN(sample_token);


CREATE TABLE IF NOT EXISTS documents.session_document(
    id serial PRIMARY KEY,
    session_id integer REFERENCES session(id) ON DELETE CASCADE,
    session_body text,
    session_token tsvector
);

CREATE INDEX IF NOT EXISTS session_document_gin ON documents.session_document USING GIN(session_token);

