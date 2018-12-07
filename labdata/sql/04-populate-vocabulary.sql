INSERT INTO vocabulary.method (id, description, authority)
SELECT id, description, 'EarthChem'
FROM earthchem_vocabulary.method
ON CONFLICT DO NOTHING;

INSERT INTO vocabulary.parameter (id, description, authority)
SELECT id, description, 'EarthChem'
FROM earthchem_vocabulary.parameter
ON CONFLICT DO NOTHING;

INSERT INTO vocabulary.unit (id, description, authority)
SELECT id, description, 'EarthChem'
FROM earthchem_vocabulary.unit
ON CONFLICT DO NOTHING;
