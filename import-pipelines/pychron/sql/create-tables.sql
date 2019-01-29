CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS method_data;

CREATE TABLE method_data.pychron_interpreted_age (
  session_id integer REFERENCES session(id),
  uid uuid PRIMARY KEY,
  data jsonb
);

CREATE VIEW method_data.ar_age AS
SELECT data FROM method_data.pychron_interpreted_age;
