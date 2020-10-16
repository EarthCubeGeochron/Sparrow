from sparrow.auth.create_user import _create_user


class TestSparrowAuth:
    def test_create_user(self, db):
        user = "Test"
        password = "test"
        _create_user(db, user, password)

    def test_login(self, client):
        res = client.post(
            "/api/v2/auth/login", data={"username": "Test", "password": "test"}
        )
