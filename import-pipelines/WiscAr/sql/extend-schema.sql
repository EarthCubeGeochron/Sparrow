/*
### Analytical Groups

Groups of sessions for import are less universally
meaningful than project-based groups. However, these
can be important for internal lab processes.
Examples include irradiation IDs for Ar/Ar labs, etc.

Right now, we only support a single measurement group
for each session. This could potentially be updated
to support a one-to-many relationship if desired.

This table was dropped from the core schema (for now) since
it is only applicable to a few use cases. Such data can also
be stored in unstructured JSONB in the `data` column that has since
been added to the core schema.
*/
CREATE TABLE IF NOT EXISTS irradiation (
  id text PRIMARY KEY,
  title text NOT NULL
);

ALTER TABLE session
 ADD COLUMN irradiation text
 REFERENCES irradiation(id);

ALTER TABLE analysis ADD COLUMN in_plateau boolean;
ALTER TABLE analysis ADD COLUMN data jsonb;

COMMIT;
