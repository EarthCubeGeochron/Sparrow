/*
Add a column for extra per-session data, organized
as unstructured JSON.
*/
ALTER TABLE session ADD COLUMN data jsonb;
ALTER TABLE analysis ADD COLUMN in_plateau boolean;
ALTER TABLE analysis ADD COLUMN data jsonb;

COMMIT;
