/** Use the With operator to create the nested tables */
DROP VIEW IF EXISTS vocabulary.metrics;
CREATE VIEW vocabulary.metrics AS 
WITH 
d AS(SELECT COUNT(DISTINCT(project.id)) number_of_projects FROM core_view.project),
c AS(SELECT COUNT(DISTINCT(sample.name)) number_of_samples FROM core_view.sample),
e AS(SELECT COUNT(DISTINCT(session.id)) number_of_Sessions FROM core_view.session),
f AS(SELECT COUNT(DISTINCT(analysis_id)) Number_Of_Analyses FROM core_view.analysis),
g AS(SELECT COUNT(DISTINCT(datum_id)) Number_of_Datum FROM core_view.datum),
b AS(SELECT COUNT(DISTINCT(sample.material)) number_of_materials FROM core_view.sample WHERE sample.material IS NOT null),
a AS (SELECT COUNT(DISTINCT(s.name)) Samples_With_Location FROM core_view.sample s WHERE s.geometry IS NOT null),
h AS (SELECT COUNT(age.value) Number_of_Plateau_Ages FROM core_view.age_context age WHERE age.parameter = 'plateau_age'),
i AS (SELECT COUNT(age.value) Number_of_Total_Fusion_Ages FROM core_view.age_context age WHERE age.parameter = 'total_fusion_age'),
j AS (SELECT array_agg(DISTINCT a.technique) techniques FROM core_view.age_datum a),
k AS (SELECT array_agg(DISTINCT a.target) targets FROM core_view.age_context a),
l AS (SELECT COUNT(DISTINCT a.geo_entity_name) Number_Of_Formations_Connected FROM core_view.age_context a)
SELECT * FROM a, b, c, d, e, f, g, h, i, j, k, l;