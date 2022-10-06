alter table "public"."__analysis_attribute" drop column "audit_id";
alter table "public"."__analysis_constant" drop column "audit_id";
alter table "public"."__session_attribute" drop column "audit_id";
alter table "public"."analysis" drop column "audit_id";
alter table "public"."attribute" drop column "audit_id";
alter table "public"."constant" drop column "audit_id";
alter table "public"."data_file" drop column "audit_id";
alter table "public"."data_file_link" drop column "audit_id";
alter table "public"."data_file_type" drop column "audit_id";
alter table "public"."datum" drop column "audit_id";
alter table "public"."datum_type" drop column "audit_id";
alter table "public"."geo_entity" drop column "audit_id";
alter table "public"."instrument" drop column "audit_id";
alter table "public"."instrument_session" drop column "audit_id";
alter table "public"."instrument_session_researcher" drop column "audit_id";
alter table "public"."project" drop column "audit_id";
alter table "public"."project_publication" drop column "audit_id";
alter table "public"."project_researcher" drop column "audit_id";
alter table "public"."project_sample" drop column "audit_id";
alter table "public"."publication" drop column "audit_id";
alter table "public"."researcher" drop column "audit_id";
alter table "public"."sample" drop column "audit_id";
alter table "public"."sample_attribute" drop column "audit_id";
alter table "public"."sample_geo_entity" drop column "audit_id";
alter table "public"."sample_publication" drop column "audit_id";
alter table "public"."sample_researcher" drop column "audit_id";
alter table "public"."session" drop column "audit_id";
alter table "public"."standard_sample" drop column "audit_id";
alter table "public"."user" drop column "audit_id";
alter table "sparrow_defs"."organization" drop column "audit_id";
alter table "tags"."analysis_tag" drop column "audit_id";
alter table "tags"."datum_tag" drop column "audit_id";
alter table "tags"."project_tag" drop column "audit_id";
alter table "tags"."sample_tag" drop column "audit_id";
alter table "tags"."session_tag" drop column "audit_id";
alter table "tags"."tag" drop column "audit_id";
alter table "vocabulary"."analysis_type" drop column "audit_id";
alter table "vocabulary"."entity_reference" drop column "audit_id";
alter table "vocabulary"."entity_type" drop column "audit_id";
alter table "vocabulary"."error_metric" drop column "audit_id";
alter table "vocabulary"."material" drop column "audit_id";
alter table "vocabulary"."material_link" drop column "audit_id";
alter table "vocabulary"."method" drop column "audit_id";
alter table "vocabulary"."parameter" drop column "audit_id";
alter table "vocabulary"."parameter_link" drop column "audit_id";
alter table "vocabulary"."unit" drop column "audit_id";