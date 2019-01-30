INSERT INTO vocabulary.error_metric (id, description, authority)
VALUES
('1σ','1 standard deviation','WiscAr'),
('2σ','2 standard deviations','WiscAr')
ON CONFLICT DO NOTHING;
