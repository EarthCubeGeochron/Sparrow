/*
## Data

Insert basic data into vocabulary tables
*/

INSERT INTO vocabulary.entity_type(id, type_of)
VALUES
  ('member', 'bedrock unit'),
  ('formation', 'bedrock unit'),
  ('group', 'bedrock unit'),
  ('supergroup', 'bedrock unit'),
  ('bedrock unit', null);

INSERT INTO vocabulary.entity_reference(id)
VALUES
  ('base'),
  ('top');
