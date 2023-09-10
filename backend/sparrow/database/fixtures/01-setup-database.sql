/*
# Database schema
*/

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- TODO: Add safeupdate to preload libraries

/*
Drop extra schemas and extensions created by PostGIS,
because they interfere with generation of migrations
*/
drop extension if exists "postgis_tiger_geocoder" CASCADE;
drop extension if exists "postgis_topology" CASCADE;
drop extension if exists "fuzzystrmatch";
drop schema if exists "tiger";
drop schema if exists "tiger_data";
drop schema if exists "topology";

-- Prepare for next version where we encapsulate all Sparrow tables in a schema
CREATE SCHEMA IF NOT EXISTS sparrow;

/*
Vocabularies
Tables to integrate units, etc.
from curated collections
*/
CREATE SCHEMA IF NOT EXISTS vocabulary;
CREATE SCHEMA IF NOT EXISTS enum;
