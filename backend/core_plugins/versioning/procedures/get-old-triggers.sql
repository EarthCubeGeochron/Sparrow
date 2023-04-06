SELECT event_object_schema schema, event_object_table table
FROM information_schema.triggers
WHERE trigger_name = 'log_insert_trigger'