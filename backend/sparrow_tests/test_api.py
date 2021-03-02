import json
from pytest import mark
from .fixtures import basic_data
from .helpers import json_fixture
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import mapping, Point
import datetime
import pdb


def create_location_from_coordinates(longitude, latitude):
    """This function will create the json-like object
    in database from long & lat given in a post request
    """
    location = from_shape(Point(longitude, latitude), srid=4326)
    return location


class TestAPIV2:
    @mark.parametrize("route", ["/api/v2", "/api/v2/"])
    def test_api_root_route(self, client, route):
        res = client.get(route)
        assert res.status_code == 200
        data = res.json()
        assert data["routes"] is not None

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

    def test_load_data(self, client, db):
        Material = db.model.vocabulary_material
        Sample = db.model.sample

        db.session.add_all(
            [
                Material(id="basalt"),
                Material(id="dacite"),
                Material(id="lava"),
            ]
        )

        db.session.commit()

        db.session.add_all(
            [
                Sample(
                    id=18,
                    name="M2C",
                    material="basalt",
                    location=create_location_from_coordinates(120, 80),
                ),
                Sample(
                    id=19,
                    name="Test_sample",
                    material="dacite",
                    location=create_location_from_coordinates(60, 30),
                ),
                Sample(
                    id=20,
                    name="Test_sample2",
                    material="lava",
                    location=create_location_from_coordinates(170, 34),
                ),
                Sample(id=21, name="Test_sample3", material="lava"),
            ]
        )

        db.session.commit()
        pass

    def test_api_datasheet(self, client, db):
        """
        Test to go along with the datasheet editor api plugin.
        """
        res_test = client.get("/api/v2/models/sample?per_page=5")
        test_sample_data = res_test.json()
        assert res_test.status_code == 200

        ## Check if data went through, both material and sample data would have to have gone through
        assert len(test_sample_data["data"]) != 0

        edited_sample_data = json_fixture("sample-edits.json")

        route = "/api/v2/datasheet/edits"
        data = {"Status": "Success"}
        res = client.post(route, json=edited_sample_data)
        assert res.status_code == 200
        assert res.json() == data

    def test_api_datasheet_view(self, db, client):
        ## first load material data and then sample data so i can have material in the sample

        route = "api/v2/datasheet/view"
        res = client.get(route)

        assert res.status_code == 200
        ##assert 0 == 1

    @mark.xfail(reason="This test seems to run before we put any data in the database.")
    def test_get_data(self, client, db):
        """Get some data for us to work with"""
        db.load_data("session", basic_data)

        res = client.get("/api/v2/models/session")
        assert res.status_code == 200
        data = res.json()
        assert (
            data["total_count"] == 1
        )  ## it fails here because theres no data. db.load_data isn't working
        assert data["data"][0]["name"] == "Declarative import test"

    def test_model_analysis(self, client, db):
        """
        Test to make sure models/analysis is working because it wasn't

        Seems to work in test...
        """

        res = client.get("/api/v2/models/analysis")
        assert res.status_code == 200
        assert 1 == 2
