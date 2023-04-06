DROP SCHEMA IF EXISTS core_view CASCADE;

UPDATE sample
SET "location" = ST_Transform("location", 4326)
WHERE ST_SRID("location") != 0;

UPDATE sample
SET "location" = ST_SetSRID("location", 4326)
WHERE ST_SRID("location") = 0;

ALTER TABLE "public"."sample" ALTER COLUMN "location" SET DATA TYPE
geometry(Point,4326) USING "location"::geometry(Point,4326);