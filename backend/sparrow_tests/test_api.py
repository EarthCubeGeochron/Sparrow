import json
from pytest import mark
from .fixtures import basic_data


class TestAPIV2:
    @mark.parametrize("route", ["/api/v2", "/api/v2/"])
    def test_api_root_route(self, client, route):
        res = client.get(route)
        assert res.status_code == 200
        data = res.json()
        assert data["routes"] is not None

    @mark.xfail(
        reason="This fails due to transaction isolation in the testing database."
    )

    @mark.parametrize("route", ["/api/v2/models/sample", "/api/v2/models/sample/"])
    def test_api_models_sample(self, client, route):
        """Checks if models/sample is working"""

        res = client.get(route)
        assert res.status_code == 200
        data = res.json()
        assert data["description"] is not None

    @mark.parametrize("route", ["/api/v2/vocabulary/metrics"])
    def test_api_metrics(self, client, route):
        """Checks to See if the Metrics API endpoint is working"""
        res = client.get(route)
        assert res.status_code == 200

    def test_api_datasheet(self, client):
        '''
        Test to go along with the datasheet editor api plugin.
            1. Add the route
            2. Create data
            3. Send the data as a post and turn data in json by the dumps method
            4. Assert that the response I get is the same as the original data
            5. Check the status code to make sure it's 200 (Working Correctly)
        '''
        route = '/api/v2/edits/datasheet'
        data = {"Status": "Success"}
        res = client.post(route, data=json.dumps(data))
        assert res.status_code == 200
        assert res.json() == data


    def test_get_data(self, client, db):
        """Get some data for us to work with"""
        db.load_data("session", basic_data)

        res = client.get("/api/v2/session")
        assert res.status_code == 200
        data = res.json()
        assert data["total_count"] == 1
        assert data["data"][0]["name"] == "Declarative import test"
