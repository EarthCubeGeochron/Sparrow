DROP TABLE IF EXISTS
  researcher,
  publication,
  project,
  project_publication,
  project_researcher,
  analysis,
  session,
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
--DROP SCHEMA vocabulary CASCADE;
DROP TABLE vocabulary.material;
CREATE SCHEMA vocabulary;

CREATE TABLE vocabulary.parameter (
  id text PRIMARY KEY,
  description text,
  authority text
);

CREATE TABLE vocabulary.material (
  id text PRIMARY KEY,
  description text,
  authority text,
  type_of text REFERENCES vocabulary.material(id)
);

CREATE TABLE vocabulary.method (
  id text PRIMARY KEY,
  description text,
  authority text
);


CREATE TABLE vocabulary.unit (
  id text PRIMARY KEY,
  description text,
  authority text
);

CREATE TABLE vocabulary.error_metric (
  id text PRIMARY KEY,
  description text,
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
  error_unit text REFERENCES vocabulary.unit(id),
  error_metric text REFERENCES vocabulary.error_metric(id),
  is_computed boolean, -- Can be rebuilt from data IN THE DATABASE
  is_interpreted boolean, -- Results from a data-reduction process
  description text,
  UNIQUE (parameter, unit, error_unit,
          error_metric, is_computed, is_interpreted)
);

CREATE TABLE sample (
  /*
  Sample: an object to be measured

  Potential issues:
  - Samples potentially have several levels of abstraction
    (e.g. different replicates or drillings from the same rock sample)
    (could have a self-referential 'part_of' relation on sample...)
  - Samples might belong to several projects
  */
  id text PRIMARY KEY,
  igsn text UNIQUE,
  project_id text REFERENCES project(id),
  material text REFERENCES vocabulary.material(id),
  location geometry
);

CREATE TABLE session (
  /* Set of analyses on the same instrument
     with the same technique, at the same or
     closely spaced in time. */
  id serial PRIMARY KEY,
  sample_id text REFERENCES sample(id),
  date timestamptz NOT NULL,
  end_date timestamptz,
  instrument integer REFERENCES instrument(id),
  technique text REFERENCES vocabulary.method(id),
  target text REFERENCES vocabulary.material(id),
  UNIQUE (sample_id, date, instrument, technique)
);

/*
SINGLE ANALYSES
These two tables will end up needing data-type specific columns
*/
CREATE TABLE analysis (
  /*
  Set of data measured together at one time on one instrument
  Example: different oxides measured on an EPMA
           are *data* in a single analysis
  */
  id serial PRIMARY KEY,
  session_id integer REFERENCES session(id) NOT NULL,
  session_index integer, -- captures ordering within a session
  date timestamptz,
  material text REFERENCES vocabulary.material(id),
  /* Not really sure that material is the best parameterization
     of this concept... */
  UNIQUE (session_id, session_index)
);

CREATE TABLE datum (
  id serial PRIMARY KEY,
  analysis integer REFERENCES analysis(id),
  type integer REFERENCES datum_type(id),
  value numeric NOT NULL,
  error numeric,
  is_bad boolean,
  UNIQUE (analysis, type)
);
