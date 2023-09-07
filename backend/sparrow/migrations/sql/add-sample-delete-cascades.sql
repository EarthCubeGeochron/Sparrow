alter table "public"."__analysis_attribute" drop constraint
"__analysis_attribute_analysis_id_fkey";
alter table "public"."__analysis_attribute" drop constraint
"__analysis_attribute_attribute_id_fkey";
alter table "public"."__analysis_constant" drop constraint
"__analysis_constant_analysis_id_fkey";
alter table "public"."__analysis_constant" drop constraint
"__analysis_constant_constant_id_fkey";
alter table "public"."__session_attribute" drop constraint
"__session_attribute_attribute_id_fkey";
alter table "public"."__session_attribute" drop constraint
"__session_attribute_session_id_fkey";
alter table "public"."sample_attribute" drop constraint
"sample_attribute_attribute_id_fkey";
alter table "public"."sample_attribute" drop constraint
"sample_attribute_sample_id_fkey";
alter table "public"."__analysis_attribute" add constraint
"__analysis_attribute_analysis_id_fkey" FOREIGN KEY (analysis_id) REFERENCES
analysis(id) ON DELETE CASCADE;
alter table "public"."__analysis_attribute" add constraint
"__analysis_attribute_attribute_id_fkey" FOREIGN KEY (attribute_id) REFERENCES
attribute(id) ON DELETE CASCADE;
alter table "public"."__analysis_constant" add constraint
"__analysis_constant_analysis_id_fkey" FOREIGN KEY (analysis_id) REFERENCES analysis(id)
ON DELETE CASCADE;
alter table "public"."__analysis_constant" add constraint
"__analysis_constant_constant_id_fkey" FOREIGN KEY (constant_id) REFERENCES constant(id)
ON DELETE CASCADE;
alter table "public"."__session_attribute" add constraint
"__session_attribute_attribute_id_fkey" FOREIGN KEY (attribute_id) REFERENCES
attribute(id) ON DELETE CASCADE;
alter table "public"."__session_attribute" add constraint
"__session_attribute_session_id_fkey" FOREIGN KEY (session_id) REFERENCES session(id) ON
DELETE CASCADE;
alter table "public"."sample_attribute" add constraint
"sample_attribute_attribute_id_fkey" FOREIGN KEY (attribute_id) REFERENCES attribute(id)
ON DELETE CASCADE;
alter table "public"."sample_attribute" add constraint "sample_attribute_sample_id_fkey"
FOREIGN KEY (sample_id) REFERENCES sample(id) ON DELETE CASCADE;
