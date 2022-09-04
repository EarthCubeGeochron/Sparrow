
CREATE SCHEMA IF NOT EXISTS sparrow_api;

CREATE OR REPLACE VIEW sparrow_api.analysis AS
SELECT * FROM core_view.analysis;