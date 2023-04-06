SELECT t.table_schema schema,
       t.table_name table
FROM information_schema.tables t
JOIN information_schema.columns c
  ON c.table_name = t.table_name 
 AND c.table_schema = t.table_schema
WHERE column_name = 'audit_id';