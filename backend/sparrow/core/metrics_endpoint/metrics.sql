WITH 
d AS(SELECT COUNT(DISTINCT(project.id)) Number_of_projects FROM core_view.project),
c AS(SELECT COUNT(DISTINCT(sample.name)) Number_of_samples FROM core_view.sample),
e AS(SELECT COUNT(DISTINCT(session.id)) Number_of_Sessions FROM core_view.session),
f AS(SELECT COUNT(DISTINCT(analysis_id)) Number_Of_Analyses FROM core_view.analysis),
g AS(SELECT COUNT(DISTINCT(datum_id)) Number_of_Datum FROM core_view.datum),
b AS(SELECT COUNT(DISTINCT(sample.material)) Number_of_materials FROM core_view.sample WHERE sample.material IS NOT null),
a AS (SELECT COUNT(DISTINCT(s.name)) Samples_With_Location FROM core_view.sample s WHERE s.geometry IS NOT null),
j AS (SELECT array_agg(DISTINCT a.technique) Techniques FROM core_view.age_datum a),
k AS (SELECT array_agg(DISTINCT a.target) Targets FROM core_view.age_context a),
l AS (SELECT COUNT(DISTINCT a.geo_entity_name) Number_Of_Formations_Connected FROM core_view.age_context a)
SELECT * FROM a, b, c, d, e, f, g, j, k, l;