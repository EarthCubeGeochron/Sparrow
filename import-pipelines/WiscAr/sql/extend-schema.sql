/*
Add a column for extra per-session data, organized
as unstructured JSON.
*/
ALTER TABLE session ADD COLUMN data jsonb;
COMMIT;
