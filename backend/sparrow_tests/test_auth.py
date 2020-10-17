from sparrow.auth.create_user import _create_user
from sparrow.auth.backend import JWTBackend
from os import environ
from pytest import fixture


@fixture(scope="class")
def auth_backend():
    return JWTBackend(environ.get("SPARROW_SECRET_KEY"))


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

    def test_invalid_token(self, client):
        pass
