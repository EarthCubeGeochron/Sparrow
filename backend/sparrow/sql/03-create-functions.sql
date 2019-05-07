CREATE OR REPLACE FUNCTION embargoed(embargo_date timestamp)
RETURNS boolean
AS $$
  SELECT coalesce(embargo_date < now(), false)
$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION embargo_date(ss sample)
RETURNS timestamp
AS $$
  SELECT coalesce(ss.embargo_date, s.embargo_date, p.embargo_date)
  FROM (SELECT (ss).*) ss
  LEFT JOIN session s
    ON ss.id = s.sample_id
  LEFT JOIN project p
    ON p.id = s.project_id
$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION embargo_date(s session)
RETURNS timestamp
AS $$
  SELECT coalesce(s.embargo_date, ss.embargo_date, p.embargo_date)
  FROM (SELECT (s).*) s
  LEFT JOIN sample ss
    ON ss.id = s.sample_id
  LEFT JOIN project p
    ON p.id = s.project_id
$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION is_public(s session)
RETURNS boolean
AS $$ SELECT NOT embargoed(embargo_date(s)) $$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION is_public(s sample)
RETURNS boolean
AS $$ SELECT NOT embargoed(embargo_date(s)) $$
LANGUAGE sql;
