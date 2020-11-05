DROP VIEW IF EXISTS vocabulary.metrics;
CREATE VIEW vocabulary.metrics AS 
SELECT COUNT(DISTINCT(material)) AS 
number_of_material FROM sample WHERE material IS NOT NULL;