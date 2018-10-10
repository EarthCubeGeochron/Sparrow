DROP TABLE
  researcher, publication, project, project_publication,
  project_researcher, sample_analysis, sample
  CASCADE;

/*
A minimal schema
*/

CREATE TABLE researcher (
  id text PRIMARY KEY,
  name text NOT NULL,
  orcid text
);

CREATE TABLE publication (
  id serial PRIMARY KEY,
  title text NOT NULL,
  doi text NOT NULL
);

-- Projects

CREATE TABLE project (
  id text PRIMARY KEY,
  title text NOT NULL,
  description text
);

CREATE TABLE project_researcher (
  project_id text REFERENCES project(id),
  researcher_id text REFERENCES researcher(id),
  PRIMARY KEY (project_id, researcher_id)
);

CREATE TABLE project_publication (
  project_id text REFERENCES project(id),
  publication_id integer REFERENCES publication(id),
  PRIMARY KEY (project_id, publication_id)
);

-- Samples

CREATE TABLE sample (
  id text PRIMARY KEY,
  project_id text REFERENCES project(id),
  location geometry
);

CREATE TABLE analysis_session (
  id serial PRIMARY KEY,
  sample_id text REFERENCES sample(id),
  date timestamp
);

-- Single analyses

CREATE TABLE analysis (
  id serial PRIMARY KEY,
  session_id integer REFERENCES analysis_session(id)
);

CREATE TABLE datum_type (
  id text PRIMARY KEY,
  description text
);

CREATE TABLE datum (
  id serial PRIMARY KEY,
  analysis integer REFERENCES analysis(id),
  type text REFERENCES datum_type(id),
  value numeric NOT NULL,
  error numeric,
  computed boolean DEFAULT false
);
