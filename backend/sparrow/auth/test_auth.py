from enum import auto
from os import environ
from pytest import fixture, mark
from .create_user import _create_user
from .backend import JWTBackend
from starlette.authentication import requires


@fixture(scope="class")
def auth_backend():
    return JWTBackend(environ.get("SPARROW_SECRET_KEY"))


def is_forbidden(res):
    data = res.json()["error"]
    return (
        res.status_code == 403
        and data["detail"] == "Forbidden"
        and data["status_code"] == 403
    )


def get_access_cookie(response):
    return {"access_token_cookie": response.cookies.get("access_token_cookie")}


def verify_credentials(client, cred):
    login = client.post("/api/v2/auth/login", json=cred)
    res = client.get("/api/v2/auth/status", cookies=get_access_cookie(login))
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == cred["username"]
    assert data["login"]
    return res


bad_credentials = [
    {"username": "TestA", "password": "test"},
    {"username": "TestA", "password": "xxxxx"},
    {"username": "", "password": ""},
    {},
    None,
]


@fixture(scope="module", autouse=True)
def setup_ws_test_route(app):
    @app.websocket_route("/ws-test")
    @requires("admin")
    async def ws_route(websocket, additional):
        await websocket.accept()
        await websocket.send_json(
            {"authenticated": websocket.user.is_authenticated, "additional": additional}
        )


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
        assert is_forbidden(res)

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

    @mark.parametrize("bad_credentials", bad_credentials)
    def test_bad_login(self, client, bad_credentials):
        res = client.post("/api/v2/auth/login", json=bad_credentials)
        assert res.status_code in [401, 422]
        if res.status_code == 401:
            assert not res.json()["login"]

    def test_invalid_token(self, client):
        res = client.get(
            "/api/v2/auth/secret", cookies={"access_token_cookie": "ekadqw4fw"}
        )
        assert is_forbidden(res)

    def test_v1_restricted(self, client):
        res = client.get("/api/v1/sample", params={"all": True})
        assert res.status_code == 200

    def test_status(self, client):
        """We should be logged out"""
        res = client.get("/api/v2/auth/status")
        assert res.status_code == 200
        data = res.json()
        assert not data["login"]
        assert data["username"] is None

    def test_login_flow(self, client):
        res = verify_credentials(client, {"username": "Test", "password": "test"})
        secret = client.get("/api/v2/auth/secret", cookies=get_access_cookie(res))
        assert secret.status_code == 200
        data = secret.json()
        assert data["answer"] == 42

    def test_invalid_login(self, client):
        try:
            res = verify_credentials(
                client, {"username": "TestAAA", "password": "test"}
            )
        except AssertionError:
            # We expect an assertion error here...
            return
        assert False

    def test_access_token(self, client):
        res = client.post(
            "/api/v2/auth/login", json={"username": "Test", "password": "test"}
        )
        data = res.json()
        assert "error" not in data

        token = data["token"]

        res = client.get("/api/v2/auth/secret")
        data = res.json()
        assert "error" not in data
        assert data["answer"] == 42
