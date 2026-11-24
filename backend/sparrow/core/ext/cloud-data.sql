-- S3 ETags are almost, but not quite, the MD5 hashes that identify data files
ALTER TABLE data_file ADD COLUMN file_etag text UNIQUE;
