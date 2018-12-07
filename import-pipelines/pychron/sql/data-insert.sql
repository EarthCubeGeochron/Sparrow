INSERT INTO method_data.pychron_interpreted_age (uid, data)
VALUES (:id, :data)
ON CONFLICT DO NOTHING
