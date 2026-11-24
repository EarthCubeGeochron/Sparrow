/*
Tables for tags backend

One table with some default tags. 
And then relationship tables similar to project_samples, project_publications...
*/
CREATE SCHEMA IF NOT EXISTS tags;

CREATE TABLE IF NOT EXISTS tags.tag (
    id serial PRIMARY KEY,
    name text,
    description text,
    color text --#RRGGBB
);

CREATE TABLE IF NOT EXISTS tags.datum_tag (
    tag_id integer REFERENCES tags.tag(id) ON DELETE CASCADE,
    datum_id integer REFERENCES datum(id) ON DELETE CASCADE,
    PRIMARY KEY(tag_id, datum_id) 
);

CREATE TABLE IF NOT EXISTS tags.analysis_tag (
    tag_id integer REFERENCES tags.tag(id) ON DELETE CASCADE,
    analysis_id integer REFERENCES analysis(id) ON DELETE CASCADE,
    PRIMARY KEY (tag_id, analysis_id)
);

CREATE TABLE IF NOT EXISTS tags.session_tag (
    tag_id integer REFERENCES tags.tag(id) ON DELETE CASCADE,
    session_id integer REFERENCES session(id) ON DELETE CASCADE,
    PRIMARY KEY(tag_id, session_id)
);

CREATE TABLE IF NOT EXISTS tags.sample_tag (
    tag_id integer REFERENCES tags.tag(id) ON DELETE CASCADE,
    sample_id integer REFERENCES sample(id) ON DELETE CASCADE,
    PRIMARY KEY(tag_id, sample_id)
);

CREATE TABLE IF NOT EXISTS tags.project_tag (
    tag_id integer REFERENCES tags.tag(id) ON DELETE CASCADE,
    project_id integer REFERENCES project(id) ON DELETE CASCADE,
    PRIMARY KEY (tag_id, project_id)
);

-- Add privileges
GRANT USAGE ON SCHEMA tags TO view_public;
GRANT SELECT ON ALL TABLES IN SCHEMA tags TO view_public;

GRANT USAGE ON SCHEMA tags TO admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA tags TO admin;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA tags TO admin;

/* Tags for PostgREST: the tags themselves, and which records carry them */
CREATE OR REPLACE VIEW sparrow_api.tag AS SELECT * FROM tags.tag;
CREATE OR REPLACE VIEW sparrow_api.sample_tag AS SELECT * FROM tags.sample_tag;
CREATE OR REPLACE VIEW sparrow_api.session_tag AS SELECT * FROM tags.session_tag;
CREATE OR REPLACE VIEW sparrow_api.project_tag AS SELECT * FROM tags.project_tag;
CREATE OR REPLACE VIEW sparrow_api.analysis_tag AS SELECT * FROM tags.analysis_tag;
CREATE OR REPLACE VIEW sparrow_api.datum_tag AS SELECT * FROM tags.datum_tag;

GRANT SELECT ON sparrow_api.tag, sparrow_api.sample_tag, sparrow_api.session_tag,
  sparrow_api.project_tag, sparrow_api.analysis_tag, sparrow_api.datum_tag
  TO view_public;
GRANT SELECT, UPDATE, INSERT, DELETE ON sparrow_api.tag, sparrow_api.sample_tag,
  sparrow_api.session_tag, sparrow_api.project_tag, sparrow_api.analysis_tag,
  sparrow_api.datum_tag
  TO admin;
