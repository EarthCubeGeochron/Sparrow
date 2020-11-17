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


INSERT INTO vocabulary.parameter(id, description, authority)
VALUES
  ('Detrital grain age', 'Crystallization age of a detrital mineral grain in sedimentary rock', 'Sparrow'),
  ('Surface exposure age', 'Duration of surface exposure to present', 'Sparrow'),
  ('Burial age', 'Age of last surface exposure', 'Sparrow'),
  ('Igneous crystallization age', 'Crystallization age of a volcanic or igneous rock', 'Sparrow')
ON CONFLICT (id) DO UPDATE SET
  description = EXCLUDED.description,
  authority = EXCLUDED.authority;
