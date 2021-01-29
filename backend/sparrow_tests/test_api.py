from pytest import mark
from .fixtures import basic_data


class TestAPIV2:
    @mark.parametrize("route", ["/api/v2", "/api/v2/"])
    def test_api_root_route(self, client, route):
        res = client.get(route)
        assert res.status_code == 200
        data = res.json()
        assert data["routes"] is not None

    @mark.parametrize("route", ["/api/v2/models/sample", "/api/v2/models/sample/"])
    def test_api_models_sample(self, client, route):
        """Checks if models/sample is working"""

        res = client.get(route)
        assert res.status_code == 200
        data = res.json()
        assert data["description"] is not None

    @mark.xfail(reason="This test seems to run before we put any data in the database.")
    def test_get_data(self, client, db):
        """Get some data for us to work with"""
        db.load_data("session", basic_data)

        res = client.get("/api/v2/models/session")
        assert res.status_code == 200
        data = res.json()
        assert data["total_count"] == 1
        assert data["data"][0]["name"] == "Declarative import test"
