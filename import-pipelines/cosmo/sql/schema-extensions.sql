ALTER TABLE sample
ADD COLUMN elevation numeric;

ALTER TABLE analysis
ADD COLUMN standard_id text;

ALTER TABLE datum
ADD COLUMN interror numeric;
