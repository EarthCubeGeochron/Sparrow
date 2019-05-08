ALTER TABLE datum_type
ADD COLUMN error_level text;

INSERT INTO vocabulary.unit (id, authority)
VALUES
('ratio', 'Boise State'),
('unknown', 'Daven Quinn')
ON CONFLICT DO NOTHING;
