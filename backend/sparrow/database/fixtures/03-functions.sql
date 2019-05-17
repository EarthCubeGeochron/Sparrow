CREATE OR REPLACE FUNCTION embargoed(embargo_date timestamp)
RETURNS boolean
AS $$
  SELECT coalesce(embargo_date > now(), false)
$$
LANGUAGE sql STABLE;

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
LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION is_public(p project)
RETURNS boolean
AS $$ SELECT NOT embargoed(p.embargo_date) $$
LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION is_public(s session)
RETURNS boolean
AS $$
BEGIN

IF (s.embargo_date IS NOT null) THEN
  RETURN NOT embargoed(s.embargo_date);
END IF;

IF (s.project_id IS NOT null) THEN
	RETURN is_public(p)
  FROM project p
  WHERE s.project_id = p.id;
END IF;

RETURN true;

END;
$$
LANGUAGE plpgsql STABLE;


CREATE OR REPLACE FUNCTION is_public(s sample)
RETURNS boolean
AS $$
BEGIN

IF (s.embargo_date IS NOT null) THEN
  RETURN NOT embargoed(s.embargo_date);
END IF;

/* A sample gains its public/private status
  primarily from whether it has any public
  sessions. */
IF (NOT EXISTS (
  SELECT sample_id FROM session WHERE sample_id = s.id)
) THEN
  RETURN true;
END IF;

RETURN EXISTS(
  SELECT sample_id
  FROM session
  WHERE sample_id = s.id
    AND is_public(session)
);

END;
$$
LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION is_public(a analysis)
RETURNS boolean
AS $$
SELECT is_public(s)
FROM session s
WHERE s.id = a.session_id;
$$
LANGUAGE sql STABLE;

CREATE OR REPLACE FUNCTION is_public(d datum)
RETURNS boolean
AS $$
BEGIN
IF (d.analysis IS NOT null) THEN
	RETURN is_public(a)
	FROM analysis a
	WHERE d.analysis = a.id;
ELSE
  RETURN true;
END IF;
END;
$$
LANGUAGE plpgsql STABLE;
