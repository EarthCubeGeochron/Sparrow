CREATE ROLE admin;
CREATE ROLE view_public;

GRANT USAGE ON SCHEMA public TO view_public;
GRANT USAGE ON SCHEMA vocabulary TO view_public;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO view_public;
GRANT SELECT ON ALL TABLES IN SCHEMA vocabulary TO view_public;

-- Lock down core tables

ALTER TABLE datum ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE session ENABLE ROW LEVEL SECURITY;
ALTER TABLE sample ENABLE ROW LEVEL SECURITY;
ALTER TABLE project ENABLE ROW LEVEL SECURITY;

-- Admin unrestricted policies
DROP POLICY IF EXISTS admin_all ON datum;
DROP POLICY IF EXISTS admin_all ON analysis;
DROP POLICY IF EXISTS admin_all ON session;
DROP POLICY IF EXISTS admin_all ON sample;
DROP POLICY IF EXISTS admin_all ON project;

CREATE POLICY admin_all
ON datum TO admin
USING (true);

CREATE POLICY admin_all
ON analysis TO admin
USING (true);

CREATE POLICY admin_all
ON session TO admin
USING (true);

CREATE POLICY admin_all
ON sample TO admin
USING (true);

CREATE POLICY admin_all
ON project TO admin
USING (true);


/* Public embargo policies */
DROP POLICY IF EXISTS public_embargo ON datum;
DROP POLICY IF EXISTS public_embargo ON analysis;
DROP POLICY IF EXISTS public_embargo ON session;
DROP POLICY IF EXISTS public_embargo ON sample;
DROP POLICY IF EXISTS public_embargo ON project;

CREATE POLICY public_embargo
ON datum
FOR SELECT
TO view_public
USING (is_public(datum));

CREATE POLICY public_embargo
ON analysis
FOR SELECT
TO view_public
USING (is_public(analysis));

CREATE POLICY public_embargo
ON session
FOR SELECT
TO view_public
USING (is_public(session));

CREATE POLICY public_embargo
ON sample
FOR SELECT
TO view_public
USING (is_public(sample));

CREATE POLICY public_embargo
ON project
FOR SELECT
TO view_public
USING (is_public(project));

/* Allow admin to do everything */
GRANT ALL ON datum TO admin;
GRANT ALL ON analysis TO admin;
GRANT ALL ON session TO admin;
GRANT ALL ON sample TO admin;
GRANT ALL ON project TO admin;

/* Allow public to select only */
GRANT SELECT ON datum TO view_public;
GRANT SELECT ON analysis TO view_public;
GRANT SELECT ON session TO view_public;
GRANT SELECT ON sample TO view_public;
GRANT SELECT ON project TO view_public;


