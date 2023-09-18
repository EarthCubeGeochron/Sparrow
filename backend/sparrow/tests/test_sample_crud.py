from datetime import datetime
from sqlalchemy.exc import ProgrammingError
from psycopg2.errors import InsufficientPrivilege


class TestSampleCRUD:
    def test_sample_loading(self, db):
        """We should be able to load already-existing values with their
        primary keys.
        """
        data = {
            "name": "Soil 003",
            "location": {"type": "Point", "coordinates": [-5, 5]},
            "sessions": [
                {
                    "date": str(datetime.now()),
                    "name": "Session primary key loading",
                    "analysis": [
                        {
                            "analysis_type": "Soil aliquot pyrolysis",
                            "session_index": 0,
                            "datum": [
                                {
                                    "value": 0.280,
                                    "error": 0.021,
                                    "type": {
                                        "parameter": "soil water content",
                                        "unit": "weight %",
                                    },
                                }
                            ],
                            "attributes": [
                                {"name": "Soil horizon", "value": "A"},
                                {"name": "Soil depth range", "value": "0-10 cm"},
                            ],
                        }
                    ],
                    "attributes": [
                        {"name": "Operator", "value": "Wendy Sørensen"},
                        {"name": "Operation mode", "value": "Vacuum stabilization"},
                    ],
                    "instrument": {"name": "Postnova AF2000"},
                }
            ],
            "attributes": [
                {"name": "Soil type", "value": "Sandy loam"},
                {"name": "Soil horizon", "value": "A"},
                {"name": "Soil depth range", "value": "0-10 cm"},
            ],
        }

        db.load_data("sample", data)

    def test_sample_deletion_unauthorized(self, db):
        """We should not be able to delete a sample without the right permissions."""

        db.session.execute("SET ROLE 'view_public'")
        Sample = db.model.sample
        model = db.session.query(Sample).filter_by(name="Soil 003").one()
        try:
            db.session.delete(model)
            assert False
        except ProgrammingError as err:
            assert isinstance(err.orig, InsufficientPrivilege)
            assert "permission denied for table sample" in str(err.orig)

    def test_sample_deletion(self, db):
        """We should be able to delete a sample and all associated data."""
        db.session.rollback()
        Sample = db.model.sample
        model = db.session.query(Sample).filter_by(name="Soil 003").one()
        db.session.delete(model)


class TestSamplePostgRESTAPI:
    # When we are including external APIs like PostgREST, we need to
    # disable the database isolation fixture, since it will prevent
    # the external API from seeing the data we have loaded.
    use_isolation = False

    def test_load_data(self, client, token):
        data = {"name": "test sample 1"}
        res = client.put(
            "/api/v2/import-data/models/sample",
            headers={"Authorization": "Bearer " + token},
            json={"data": data, "filename": None},
        )
        assert res.status_code == 200

    def test_postgrest_api_accessible(self, pg_api):
        """We should be able to access the PostgREST API."""
        res = pg_api.get("/")
        assert res.status_code == 200

    def test_sample_api_get(self, pg_api):
        """We should be able to delete a sample via the API."""
        res = pg_api.get("/sample", params={"name": "eq.test sample 1"})
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        name = data[0]["name"]
        assert name == "test sample 1"

    def test_sample_api_delete_failed(self, pg_api):
        """We should be prevented from deleting a sample via API without the right permissions."""
        res = pg_api.delete("/sample", params={"name": "eq.test sample 1"})
        assert res.status_code == 401
        data = res.json()
        assert data["message"] == "permission denied for view sample"

    def test_sample_api_delete_authenticated(self, pg_api, token):
        res = pg_api.delete(
            "/sample",
            params={"name": "eq.test sample 1"},
            headers={"Authorization": "Bearer " + token},
        )
        assert res.status_code == 204

    def test_sample_was_deleted(self, pg_api):
        res = pg_api.get("/sample", params={"name": "eq.test sample 1"})
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 0
