ALTER TABLE datum_type
ADD COLUMN error_level text;

ALTER TABLE session ADD COLUMN igsn text;

INSERT INTO vocabulary.unit (id, authority)
VALUES
('ratio', 'Boise State'),
('Ma', 'Boise State'),
('unknown', 'Daven Quinn')
ON CONFLICT DO NOTHING;
