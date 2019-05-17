CREATE ROLE admin;
CREATE ROLE view_all;
CREATE ROLE view_public;

-- Lock down core tables
ALTER TABLE datum ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE session ENABLE ROW LEVEL SECURITY;
ALTER TABLE sample ENABLE ROW LEVEL SECURITY;
ALTER TABLE project ENABLE ROW LEVEL SECURITY;

-- Admin unrestricted policies
-- CREATE POLICY admin_all
-- ON (datum, analysis, session, sample, project)
-- TO admin
-- USING (true);
--
--
-- CREATE POLICY datum_public_embargo
-- ON datum
-- TO view_public
-- FOR SELECT
-- USING (is_public(ROW()*))
