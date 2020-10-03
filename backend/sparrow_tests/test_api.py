from starlette.testclient import TestClient
from sparrow.asgi import app
from pytest import fixture, mark
from .fixtures import basic_data


@fixture
def client():
    # app = construct_app()
    _client = TestClient(app)
    yield _client


class TestAPIV2:
    @mark.parametrize("route", ["/api/v2", "/api/v2/"])
    def test_api_root_route(self, client, route):
        res = client.get(route)
        assert res.status_code == 200
        data = res.json()
        assert data["routes"] is not None

    @mark.xfail(
        reason="This fails due to transaction isolation in the testing database."
    )
    def test_get_data(self, client, db):
        """Get some data for us to work with"""
        db.load_data("session", basic_data)

        res = client.get("/api/v2/session")
        assert res.status_code == 200
        data = res.json()
        assert data["total_count"] == 1
        assert data["data"][0]["name"] == "Declarative import test"
