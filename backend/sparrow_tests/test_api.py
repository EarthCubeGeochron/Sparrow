import json
from pytest import mark
from .fixtures import basic_data
from .helpers import json_fixture



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


    def test_load_sample(self, client, db):
        sample_test_data = json_fixture("sample-simple-test.json")
        db.load_data("sample", sample_test_data)

        db.exec_sql_text("INSERT INTO sample (id, name) VALUES (18, 'M2C'),(19, 'Test_sample')")

        res_test = client.get("/api/v2/models/sample?per_page=5")
        test_sample_data = res_test.json()
        assert res_test.status_code == 200


    def test_api_datasheet(self, client, db):
        """
        Test to go along with the datasheet editor api plugin.

        in the database, material has a foreign key constraint, vocabulary.material.id (which is the name, i.e basalt) 

        some helpful session func:
            session.new : shows pending objects in a session
            session.dity : shows modifications to persistant objects
            session.commit() : commits everything in session que
            session.add/add_all: pass a class and values ex: Users(firstname='Casey')
        
        Remember that session doesn't connect to database until specified to do so.
        on a query if you don't call a chain method (i.e .one(), .first(), .all()) you will
        only have a query object.

        """
        ## Attempt to load data from fixture into test database, does not work
        sample_test_data = json_fixture("sample-simple-test.json")
        db.load_data("sample", sample_test_data) ## See What's going on inside load_data

        db.exec_sql_text("INSERT INTO sample (id, name) VALUES (18, 'M2C'),(19, 'Test_sample')")

        res_test = client.get("/api/v2/models/sample?per_page=5")
        test_sample_data = res_test.json()
        assert res_test.status_code == 200

        edited_sample_data = json.dumps({
                "name": "M2C_add",
                "id": 18})

      

        route = '/api/v2/edits/datasheet'
        data = {"Status": "Success"}
        res = client.post(route, json=edited_sample_data)
        assert res.status_code == 200
        assert res.text == "M2C"


    def test_get_data(self, client, db):
        """Get some data for us to work with"""
        db.load_data("session", basic_data)

        res = client.get("/api/v2/models/session?per_page=5")
        assert res.status_code == 200
        data = res.json()
        assert data["total_count"] == 1 ## it fails here because theres no data. db.load_data isn't working
        assert data["data"][0]["name"] == "Declarative import test"
