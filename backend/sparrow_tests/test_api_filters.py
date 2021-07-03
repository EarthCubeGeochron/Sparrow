from .helpers import json_fixture
from sparrow.api.endpoints.utils import create_location_from_coordinates
from sparrow.api.utils import nested_collection_joins, nested_collection_path
from sparrow.database.util import get_db_model
from pytest import mark
import datetime
import json


class TestAPIV2_filters:
    def test_join_functions(self, client, db):
        """some sanity checks"""
        start = "sample"
        end = "datum"

        Sample = db.model.sample

        path = nested_collection_path(start, end)

        assert path == ["sample", "session", "analysis", "datum"]

        query = db.session.query(Sample)

        _query = nested_collection_joins(path, query, db, Sample)

        sql_string = str(_query)

        assert "JOIN" in sql_string
        for model in path:
            assert model in sql_string

    @mark.skip(
        reason="For some reason, this breaks project_import tests later in the sequence"
    )
    def test_load_data(self, client, db):
        Material = get_db_model(db, "vocabulary_material")
        Sample = get_db_model(db, "sample")

        db.session.add_all(
            [Material(id="basalt"), Material(id="dacite"), Material(id="lava")]
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

        Session = get_db_model(db, "session")

        date = datetime.datetime(2013, 3, 12)
        date1 = datetime.datetime(2013, 6, 1)
        date2 = datetime.datetime(2014, 6, 3)

        db.session.add_all(
            [Session(date=date), Session(date=date1), Session(date=date2)]
        )
        db.session.commit()

        # %Y-%m-%d/%H:%M:%S
        response = client.get("/api/v2/models/session?date_range=2012-01-12,2015-01-01")

        assert len(response.json()["data"]) == 3

    @mark.skip(reason="Needs previous test results to function")
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
        data = json_fixture("projects-post.json")
        db.load_data("project", data[0])

        pub_res = client.get("/api/v2/models/publication?doi_like=10.10")
        pub_json = pub_res.json()
        assert pub_json["total_count"] != 0

        proj_res = client.get("api/v2/models/project?doi_like=10.10")
        proj_json = proj_res.json()
        assert proj_json["total_count"] != 0
