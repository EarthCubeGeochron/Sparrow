from starlette.testclient import TestClient
from sparrow.asgi import app
from pytest import fixture


@fixture
def client():
    _client = TestClient(app)
    yield _client


class TestAPIV2:
    def test_api_import(self, client):
        res = client.get("/api/v2/")
        assert res.status_code == 200
        data = res.json()
        assert data["Hello"] == "world!"
