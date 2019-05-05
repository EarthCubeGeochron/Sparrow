/*
A minimal schema
*/

CREATE TABLE IF NOT EXISTS researcher (
  id integer PRIMARY KEY,
  name text NOT NULL,
  orcid text UNIQUE
);

/*
The `user` model parallels the
`researcher` model but used only for application
authentication. We can reset all application access by
truncating this table, without losing data.
*/
CREATE TABLE IF NOT EXISTS "user" ( -- Name must be quoted because it collides with reserved word.
  username text PRIMARY KEY,
  /* Stores a hashed password */
  password text,
  researcher_id integer REFERENCES researcher(id)
);

CREATE TABLE IF NOT EXISTS publication (
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

CREATE TABLE IF NOT EXISTS vocabulary.parameter (
  id text PRIMARY KEY,
  description text,
  authority text
);

CREATE TABLE IF NOT EXISTS vocabulary.material (
  id text PRIMARY KEY,
  description text,
  authority text,
  type_of text REFERENCES vocabulary.material(id)
);

CREATE TABLE IF NOT EXISTS vocabulary.method (
  id text PRIMARY KEY,
  description text,
  authority text
);


CREATE TABLE IF NOT EXISTS vocabulary.unit (
  id text PRIMARY KEY,
  description text,
  authority text
);

CREATE TABLE IF NOT EXISTS vocabulary.error_metric (
  id text PRIMARY KEY,
  description text,
  authority text
);


-- Projects

CREATE TABLE IF NOT EXISTS project (
  id text PRIMARY KEY,
  title text NOT NULL,
  description text,
  embargo_date timestamp without time zone
);

CREATE TABLE IF NOT EXISTS project_researcher (
  project_id text REFERENCES project(id),
  researcher_id integer REFERENCES researcher(id),
  PRIMARY KEY (project_id, researcher_id)
);

CREATE TABLE IF NOT EXISTS project_publication (
  project_id text REFERENCES project(id),
  publication_id integer REFERENCES publication(id),
  PRIMARY KEY (project_id, publication_id)
);

/*
### Analytical Groups

Groups of sessions for import are less universally
meaningful than project-based groups. However, these
can be important for internal lab processes.
Examples include irradiation IDs for Ar/Ar labs, etc.

Right now, we only support a single measurement group
for each session. This could potentially be updated
to support a one-to-many relationship if desired.
*/
CREATE TABLE IF NOT EXISTS measurement_group (
  id text PRIMARY KEY,
  title text NOT NULL
);

-- Descriptors for types of measurements/techniques

CREATE TABLE IF NOT EXISTS instrument (
  id serial PRIMARY KEY,
  name text UNIQUE NOT NULL,
  description text
);

CREATE TABLE IF NOT EXISTS datum_type (
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

/*
## Sample

An object to be measured
*/
CREATE TABLE IF NOT EXISTS sample (
  id text PRIMARY KEY,
  igsn text UNIQUE,
  material text REFERENCES vocabulary.material(id),
  /* Order-of-magnitude precision (in meters)
     with which this position
     is known */
  location_precision integer DEFAULT 0,
  /* A representative named location */
  location_name text,
  location geometry
);
/*
#### Potential issues:

- Samples potentially have several levels of abstraction
  (e.g. different replicates or drillings from the same rock sample)
  (could have a self-referential 'part_of' relation on sample...)
- Samples might belong to several projects

Should the `session` table contain the link to project rather than
the `sample` table? This might be more correct, and samples could still
be linked to projects through a table relationship

## Session

Set of analyses on the same instrument
with the same technique, at the same or
closely spaced in time.

#### Examples:

- An entire Ar/Ar step heating experiment
- A set of detrital single-crystal zircon measurements
- A multi-grain igneous age determination
*/
CREATE TABLE IF NOT EXISTS session (
  id serial PRIMARY KEY,
  sample_id text REFERENCES sample(id),
  project_id text REFERENCES project(id),
  measurement_group_id text REFERENCES measurement_group(id),
  date timestamptz NOT NULL,
  end_date timestamptz,
  instrument integer REFERENCES instrument(id),
  technique text REFERENCES vocabulary.method(id),
  target text REFERENCES vocabulary.material(id),
  embargo_date timestamp without time zone,
  /* A field to store extra, unstructured session data */
  data jsonb,
  UNIQUE (sample_id, date, instrument, technique)
);

/*
## Single analyses

These two tables will end up needing data-type specific columns

### `analysis`

Set of data measured together at one time on one instrument

#### Examples:

- A single EPMA analytical spot
  (different oxides measured on an EPMA are *data* in a single analysis)
- A heating step for Ar/Ar age determination
- A single-crystal zircon age measurement

*/
CREATE TABLE IF NOT EXISTS analysis (
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
  in_plateau boolean,
  /*
  Some analytical results can be interpreted from other data, so we
  should explicitly state that this is the case.

  #### Examples:

  - a detrital zircon age spectrum
    (the `datum` table would contain individual probability values at each age)
  - a multi-zircon igneous age
    (the `datum` table would include jointly-fitted age determinations
     for each relevant system)
  - a calculated plateau age for a stepped-heating Ar-Ar experiment.

  */
  is_interpreted boolean,
  data jsonb,
  UNIQUE (session_id, session_index, analysis_type)
);

CREATE TABLE IF NOT EXISTS datum (
  id serial PRIMARY KEY,
  analysis integer REFERENCES analysis(id),
  type integer REFERENCES datum_type(id),
  value numeric NOT NULL,
  error numeric,
  is_bad boolean,
  /*
  If set, this means that this is an "accepted" value
  among several related measurements.

  #### Examples:

  - Accepted system for U-Pb single-zircon age

  */
  is_accepted boolean,
  UNIQUE (analysis, type)
);

/*
## Analytical constants

Constants, etc. used in measurements, and their relationships
to individual analytical sessions, etc.

Right now, we support linking these parameters at the session
level. Some coarser (e.g. a table for analytical process) or finer
(linked parameters for each datum) abstraction might be desired.

In many ways, the column layout mirrors that of the datum table,
with the exception that there is a many-to-many link on the data.
*/
CREATE TABLE IF NOT EXISTS session_datum (
  /*
  Handles many-to-many links between session and datum, which
  is primarily useful for handling analytical parameters
  that remain constant across many sessions.
  */
  session_id integer REFERENCES session(id),
  datum_id integer REFERENCES datum(id)
);

CREATE TABLE IF NOT EXISTS data_file_type (
  id serial,
  name text,
  description text
);

CREATE TABLE IF NOT EXISTS data_file (
  /*
  Original measurement data file information
  */
  hash uuid PRIMARY KEY, -- MD5 hash of data file contents
  basename text,
  import_date timestamp,
  /*
  Foreign key columns to link to data that was imported from
  this file; this should be done at the appropriate level (e.g.
  sample, analysis, session) that fits the data file in question.
  */
  session_id integer REFERENCES session(id),
  analysis_id integer REFERENCES analysis(id),
  sample_id integer REFERENCES sample(id)
);
