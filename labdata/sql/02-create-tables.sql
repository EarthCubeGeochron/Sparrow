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
  description text,
  embargo_date timestamptz
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

  Should the `session` table contain the link to project rather than
  the `sample` table? This might be more correct -- samples could still
  be linked to projects through a table relationship
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
     closely spaced in time.

     Examples:
     - An entire Ar/Ar step heating experiment
     - A set of detrital single-crystal zircon measurements
     - A multi-grain igneous age determination
  */
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
ANALYTICAL CONSTANTS
Constants, etc. used in measurements, and their relationships
to individual analytical sessions, etc.

Right now, we support linking these parameters at the session
level. Some coarser (e.g. a table for analytical process) or finer
(linked parameters for each datum) abstraction might be desired.

In many ways, the column layout mirrors that of the datum table,
with the exception that there is a many-to-many link on the data.
*/
CREATE TABLE session_datum (
  /* Handles many-to-many links between session and datum, which
     is primarily useful for handling analytical parameters
     that remain constant for many sessions.
  */
  session_id integer REFERENCES session(id),
  datum_id integer REFERENCES datum(id)
);

/*
SINGLE ANALYSES
These two tables will end up needing data-type specific columns
*/
CREATE TABLE analysis (
  /*
  Set of data measured together at one time on one instrument
  Examples:
  - A single EPMA analytical spot
    (different oxides measured on an EPMA are *data* in a single analysis)
  - A heating step for Ar/Ar age determination
  - A single-crystal zircon age measurement
  */
  id serial PRIMARY KEY,
  session_id integer REFERENCES session(id) NOT NULL,
  session_index integer, -- captures ordering within a session
  analysis_type text,
  /* If `session_index` is not set, `analysis_type` allows the
    unique identification of a record within the session */
  date timestamptz,
  material text REFERENCES vocabulary.material(id),
  /* Not really sure that material is the best parameterization
     of this concept... */
  is_standard boolean,
  /*
  Some analytical results can be interpreted from other data, so we
  should explicitly state that this is the case.

  Examples:
  - a detrital zircon age spectrum
    (the `datum` table would contain individual probability values at each age)
  - a multi-zircon igneous age
    (the `datum` table would include jointly-fitted age determinations
     for each relevant system)
  - a calculated plateau age for a stepped-heating Ar-Ar experiment.

  */
  is_interpreted boolean,
  UNIQUE (session_id, session_index, analysis_type)
);

CREATE TABLE datum (
  id serial PRIMARY KEY,
  analysis integer REFERENCES analysis(id),
  type integer REFERENCES datum_type(id),
  value numeric NOT NULL,
  error numeric,
  is_bad boolean,
  /*
  If set, this means that this is an "accepted" value
  among several related measurements.
  Examples:
  - Accepted system for U-Pb single-zircon age
  */
  is_accepted boolean,
  UNIQUE (analysis, type)
);
