/*
# Database schema
*/

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
/*
Vocabularies
Tables to integrate units, etc.
from curated collections
*/
CREATE SCHEMA IF NOT EXISTS vocabulary;
