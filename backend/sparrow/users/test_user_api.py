from pytest import fixture
from sparrow.auth.test_auth import is_forbidden
from sparrow.auth.create_user import _create_user


@fixture(scope="class")
def admin_client(db, client):
    user = "Test"
    password = "test"
    # Create a user directly on the database
    _create_user(db, user, password)
    client.post("/api/v2/auth/login", json={"username": user, "password": password})
    return client


class TestUserAPI:
    prefix = "/api/v2"
    cookies = {}

    def test_list_users_unauthorized(self, client):
        res = client.get(self.prefix + "/users/")
        assert is_forbidden(res)

    def test_list_users_authorized(self, admin_client):
        res = admin_client.get(self.prefix + "/users/")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1