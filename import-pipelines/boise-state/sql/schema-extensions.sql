ALTER TABLE datum_type
ADD COLUMN error_level text;

ALTER TABLE session ADD COLUMN igsn text;

INSERT INTO vocabulary.unit (id, authority)
VALUES
('ratio', 'Boise State'),
('Ma', 'Boise State'),
('unknown', 'Daven Quinn')
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS igsn_data (
  igsn text PRIMARY KEY,
  import_date timestamp DEFAULT now(),
  data jsonb
);
