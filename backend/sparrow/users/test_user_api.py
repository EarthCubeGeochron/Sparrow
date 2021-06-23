from pytest import fixture
from sparrow.auth.test_auth import is_forbidden, verify_credentials
from sparrow.auth.create_user import _create_user
from starlette.testclient import TestClient
from sparrow.database.models import User


@fixture(scope="class")
def admin_client(app, db):
    user = "Test"
    password = "test"
    client = TestClient(app)
    # Create a user directly on the database
    _create_user(db, user, password)
    client.post("/api/v2/auth/login", json={"username": user, "password": password})
    return client


user2 = {"username": "quartz", "password": "silica-rocks"}


def user_exists(db, username):
    return db.session.query(User).get(username) is not None


class TestUserAPI:
    prefix = "/api/v2/users"
    cookies = {}

    def route(self, path):
        return self.prefix + path

    def test_list_users_unauthorized(self, client):
        res = client.get(self.route("/"))
        assert is_forbidden(res)

    def test_list_users(self, admin_client):
        res = admin_client.get(self.route("/"))
        assert res.status_code == 200
        data = res.json()["data"]
        assert len(data) == 1

        assert data[0]["username"] == "Test"
        assert "password" not in data[0]

    def test_create_user_unauthorized(self, client):
        res = client.post(self.route("/"), json=user2)
        assert is_forbidden(res)

    def test_create_user(self, admin_client, db):
        res = admin_client.post(self.route("/"), json=user2)
        data = res.json()["data"]
        assert data["username"] == user2["username"]
        assert "password" not in data
        assert user_exists(db, user2["username"])

    def test_failed_delete_self(self, admin_client, db):
        res = admin_client.delete(self.route("/Test"))
        assert res.status_code == 403
        assert user_exists(db, "Test")

    def test_failed_delete_unauthorized(self, client, db):
        res = client.delete(self.route("/" + user2["username"]))
        assert is_forbidden(res)
        assert user_exists(db, user2["username"])

    def test_list_users_again(self, admin_client):
        res = admin_client.get(self.route("/"))
        data = res.json()["data"]
        assert len(data) == 2
        assert data[1]["username"] == user2["username"]

    def test_delete(self, admin_client):
        res = admin_client.delete(self.route("/" + user2["username"]))
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["success"]
        assert data["deleted"][0] == user2["username"]

    def test_update_password(self, admin_client):
        _new_password = "the-dude-abides"
        res = admin_client.put(self.route("/Test"), json={"password": _new_password})
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["username"] == "Test"
        assert "password" not in data

        verify_credentials(
            admin_client, {"username": "Test", "password": _new_password}
        )
