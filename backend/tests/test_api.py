from starlette.testclient import TestClient
from sparrow.asgi import app
from pytest import fixture, mark


@fixture
def client():
    _client = TestClient(app)
    yield _client


class TestAPIV2:
    @mark.parametrize("route", ["/api/v2", "/api/v2/"])
    def test_api_root_route(self, client, route):
        res = client.get(route)
        assert res.status_code == 200
        data = res.json()
        assert data["Hello"] == "world!"
