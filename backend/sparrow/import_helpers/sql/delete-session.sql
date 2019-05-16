DELETE
FROM session s
USING import_tracker d
WHERE d.file_hash = :file_hash
  AND d.session_id = s.id;
