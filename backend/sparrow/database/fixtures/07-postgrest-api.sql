
CREATE SCHEMA IF NOT EXISTS sparrow_api;

CREATE OR REPLACE VIEW sparrow_api.analysis AS
SELECT * FROM core_view.analysis;

CREATE OR REPLACE VIEW sparrow_api.datum AS
SELECT * FROM core_view.datum;

CREATE OR REPLACE VIEW sparrow_api.attribute AS
SELECT * FROM core_view.attribute;

CREATE OR REPLACE VIEW sparrow_api.project AS
SELECT * FROM core_view.project;

CREATE OR REPLACE VIEW sparrow_api.session AS
SELECT * FROM core_view.session;