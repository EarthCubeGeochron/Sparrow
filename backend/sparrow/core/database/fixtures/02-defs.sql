CREATE SCHEMA IF NOT EXISTS sparrow_defs;

CREATE TABLE IF NOT EXISTS sparrow_defs.organization (
  name text PRIMARY KEY,
  site text NOT NULL,
  description text
);