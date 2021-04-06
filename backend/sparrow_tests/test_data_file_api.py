"""
Tests for importing data files via the API
"""
from sparrow.util import relative_path
from .helpers import json_fixture


class TestDataFileAPI:
    def test_file_import(self, client):
        """Uploads a file but doesn't do anything with it yet"""
        filename = "simple-sims-session.json"
        pth = relative_path(__file__, "fixtures", filename)

        files = {"upload_file": open(pth, "rb")}
        res = client.post("/api/v2/data_file_new", files=files, allow_redirects=True)
        data = res.json()
        assert data["success"] == True
        assert data["filename"] == filename

    def test_api_import(self, client):
        data = json_fixture("simple-sims-session.json")
        res = client.put("/api/v1/import-data/session", json={"filename": None, "data": data})
        assert res.status_code == 201