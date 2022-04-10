DELETE
FROM session s
USING data_file_link d
WHERE d.file_hash = :file_hash
  AND d.session_id = s.id;
