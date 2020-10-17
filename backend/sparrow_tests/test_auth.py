from sparrow.auth.create_user import _create_user
from sparrow.auth.backend import JWTBackend
from os import environ
from pytest import fixture


@fixture(scope="class")
def auth_backend():
    return JWTBackend(environ.get("SPARROW_SECRET_KEY"))


def check_forbidden(res):
    assert res.status_code == 403
    data = res.json()["error"]
    assert data["detail"] == "Forbidden"
    assert data["status_code"] == 403


class TestSparrowAuth:
    def test_create_user(self, db):
        user = "Test"
        password = "test"
        _create_user(db, user, password)

    def test_jwt_encoding(self, auth_backend):
        value = "Test123"
        token = auth_backend._encode(payload=dict(value=value))
        res = auth_backend._decode(token)
        assert res["value"] == value

    def ensure_user_created(self, db):
        user = db.session.query(db.model.user).get("Test")
        assert user.username == "Test"

    def test_forbidden(self, client):
        res = client.get("/api/v2/auth/secret")
        check_forbidden(res)

    def test_login(self, client, auth_backend):
        res = client.post(
            "/api/v2/auth/login", json={"username": "Test", "password": "test"}
        )
        data = res.json()
        assert "error" not in data
        assert data["username"] == "Test"
        assert data["login"]
        for type in ("access", "refresh"):
            token = res.cookies.get(f"{type}_token_cookie")
            payload = auth_backend._decode(token)
            assert payload.get("type") == type
            assert payload.get("identity") == "Test"

    def test_bad_login(self, client):
        res = client.post(
            "/api/v2/auth/login", json={"username": "TestA", "password": "test"}
        )
        assert res.status_code == 401
        assert res.json()["login"] == False

    def test_invalid_token(self, client):
        res = client.get(
            "/api/v2/auth/secret", cookies={"access_token_cookie": "ekadqw4fw"}
        )
        check_forbidden(res)

    def test_v1_restricted(self, client):
        res = client.get("/api/v1/sample", params={"all": True})
        assert res.status_code == 200
