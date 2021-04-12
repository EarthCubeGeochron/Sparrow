

class TestOpenSearch:
    def test_get_endpoint(self, client, db):
        res = client.get("api/v2/search?query=lava")

        assert 0 == 1