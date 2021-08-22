from pytest import fixture
from sparrow.auth.test_auth import is_forbidden, verify_credentials, admin_client
from sparrow.database.models import User


def user_exists(db, username):
    return db.session.query(User).get(username) is not None


user2_data = {"username": "quartz", "password": "silica-rocks"}


@fixture(scope="class")
def api_created_user(admin_client):
    res = admin_client.post("/api/v2/users/", json=user2_data)
    data = res.json()["data"]
    assert data["username"] == user2_data["username"]
    return data


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
        res = client.post(self.route("/"), json=user2_data)
        assert is_forbidden(res)

    def test_create_user(self, db, api_created_user):
        assert user_exists(db, api_created_user["username"])

    def test_password_omitted(self, api_created_user):
        assert "password" not in api_created_user

    def test_failed_delete_self(self, admin_client, db):
        res = admin_client.delete(self.route("/Test"))
        assert res.status_code == 403
        assert user_exists(db, "Test")

    def test_failed_delete_unauthorized(self, client, db, api_created_user):
        res = client.delete(self.route("/" + api_created_user["username"]))
        assert is_forbidden(res)
        assert user_exists(db, api_created_user["username"])

    def test_list_users_again(self, admin_client, api_created_user):
        res = admin_client.get(self.route("/"))
        data = res.json()["data"]
        assert len(data) == 2
        assert data[1]["username"] == api_created_user["username"]

    def test_delete(self, admin_client, api_created_user):
        res = admin_client.delete(self.route("/" + api_created_user["username"]))
        assert res.status_code == 200
        data = res.json()
        assert data["success"]
        assert data["deleted"][0] == api_created_user["username"]

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
