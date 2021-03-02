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


class TestAPIV2_filters:
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

    def test_date_filter(self, client, db):
        """Testing the date_range filter on the api"""

        Session = db.model.session

        date = datetime.datetime(2013, 3, 12)
        date1 = datetime.datetime(2013, 6, 1)
        date2 = datetime.datetime(2014, 6, 3)

        db.session.add_all(
            [
                Session(date=date),
                Session(date=date1),
                Session(date=date2),
            ]
        )
        db.session.commit()

        # %Y-%m-%d/%H:%M:%S
        response = client.get("/api/v2/models/session?date_range=2012-01-12,2015-01-01")

        assert len(response.json()["data"]) == 3

    def test_location_filters(self, client, db):
        """
        Testing the coordinate filter and the WKT geometry Filter
        """

        coord_response = client.get("/api/v2/models/sample?coordinates=-180,-90,180,90")
        coord_data = coord_response.json()
        assert coord_data["total_count"] != 0

        geometry_response = client.get(
            "/api/v2/models/sample?geometry=POLYGON((0 0 ,180 90, 0 90, 180 0, 0 0))"
        )
        geom_data = geometry_response.json()

        assert geom_data["total_count"] != 0

    def test_doi_filter(self, client, db):
        data = json_fixture("project-doi-fixes.json")
        db.load_data("project", data["data"])

        pub_res = client.get("/api/v2/models/publication?doi_like=10.10")
        pub_json = pub_res.json()
        assert pub_json["total_count"] != 0

        proj_res = client.get("api/v2/models/project?doi_like=10.10")
        proj_json = proj_res.json()
        assert proj_json["total_count"] != 0
