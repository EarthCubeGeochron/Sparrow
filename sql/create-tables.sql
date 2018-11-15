DROP TABLE IF EXISTS
  researcher,
  publication,
  project,
  project_publication,
  project_researcher,
  analysis,
  analysis_session,
  sample,
  technique,
  instrument,
  datum,
  datum_type
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

/*
Vocabularies
Tables to integrate units, etc.
from curated collections
*/
DROP SCHEMA vocabulary CASCADE;
CREATE SCHEMA vocabulary;

CREATE TABLE vocabulary.parameter (
  id text PRIMARY KEY,
  description text,
  authority text
);

CREATE TABLE vocabulary.method (
  id text PRIMARY KEY,
  description text,
  authority text
);


CREATE TABLE vocabulary.unit (
  id text PRIMARY KEY,
  authority text
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

-- Descriptors for types of measurements/techniques

CREATE TABLE instrument (
  id serial PRIMARY KEY,
  name text UNIQUE NOT NULL,
  description text
);

CREATE TABLE datum_type (
  id serial PRIMARY KEY,
  parameter text REFERENCES vocabulary.parameter(id) NOT NULL,
  unit text REFERENCES vocabulary.unit(id) NOT NULL,
  error_unit text REFERENCES vocabulary.unit(id)
);

-- Samples

CREATE TABLE sample (
  id text PRIMARY KEY,
  igsn text UNIQUE,
  project_id text REFERENCES project(id),
  location geometry
);

CREATE TABLE analysis_session (
  /* Set of analyses on the same instrument
     with the same technique, at the same or
     closely spaced in time. */
  id serial PRIMARY KEY,
  sample_id text REFERENCES sample(id),
  date timestamptz NOT NULL,
  end_date timestamptz,
  instrument integer REFERENCES instrument(id),
  technique text REFERENCES vocabulary.method(id)
);

/*
SINGLE ANALYSES
These two tables will end up needing data-type specific columns
*/
CREATE TABLE analysis (
  -- Set of data measured together at one time on one instrument
  -- Ex: different oxides measured on an EPMA are *data* in a single analysis
  id serial PRIMARY KEY,
  session_id integer REFERENCES analysis_session(id),
  date timestamptz
);

CREATE TABLE datum (
  id serial PRIMARY KEY,
  analysis integer REFERENCES analysis(id),
  type integer REFERENCES datum_type(id),
  value numeric NOT NULL,
  error numeric
);
