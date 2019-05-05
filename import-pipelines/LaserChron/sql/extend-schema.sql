INSERT INTO data_file_type (name) VALUES
  ('ETAgeCalc'),
  ('NuAgeCalc');

/* Add a column for a cached CSV representation of data table
  so we don't have to carry along the entire ETAgeCalc/
  NuAgeCalc apparatus in memory */
ALTER TABLE data_file ADD COLUMN csv_data bytea;
