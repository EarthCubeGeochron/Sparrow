DROP SCHEMA core_view CASCADE;
DROP SCHEMA enum CASCADE;
DROP SCHEMA vocabulary CASCADE;

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
