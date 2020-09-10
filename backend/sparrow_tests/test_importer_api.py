from sparrow.app import App
from sqlalchemy import and_
from datetime import datetime
from pytest import mark, fixture
import logging
from sparrow.logs import get_logger
from .fixtures import basic_data, basic_d18O_data
from .helpers import json_fixture

log = get_logger(__name__)


@fixture
def client():
    app = App(__name__)
    app.load()
    app.load_phase_2()
    with app.test_client() as client:
        yield client


class TestAPIImporter:
    def test_api_import(self, client):
        res = client.put(
            "/api/v1/import-data/session", json={"filename": None, "data": basic_data}
        )
        assert res.status_code == 201

    def test_basic_import(self, client):
        res = client.put("/api/v1/import-data/session", json=basic_d18O_data)
        assert res.status_code == 201

    @mark.skip
    def test_complex_single_row_prior(self, client, db):
        # This test fails if before the overall import
        # Too much output
        # logging.disable(logging.CRITICAL)

        complex_data = json_fixture("large-test.json")
        complex_data["data"]["analysis"] = complex_data["data"]["analysis"][2:3]

        db.load_data("session", complex_data["data"])

    def test_complex_import(self, client, db):
        # Too much output
        logging.disable(logging.DEBUG)

        complex_data = json_fixture("large-test.json")
        db.load_data("session", complex_data["data"])

        a = db.model.analysis
        q = db.session.query(a).filter(
            and_(a.session_index is not None, a.analysis_type == "d18O measurement")
        )
        assert q.count() > 1

    def test_complex_single_row(self, client, db):
        # This test fails if before the overall import
        # Too much output
        # logging.disable(logging.CRITICAL)

        complex_data = json_fixture("large-test.json")
        complex_data["data"]["analysis"] = complex_data["data"]["analysis"][3:4]

        db.load_data("session", complex_data["data"])

    def test_missing_field(self, client, db):
        """Missing fields should produce a useful error message
           and insert no data"""
        new_name = "Test error vvv"
        data = {
            "date": str(datetime.now()),
            "name": "Session with existing instances",
            "sample": {"name": new_name},
            "analysis": [
                {
                    # Can't seem to get or create this instance from the database
                    "analysis_type": "Stable isotope analysis",
                    "session_index": 0,
                    "datum": [
                        {
                            "value": 0.1,
                            "error": 0.025,
                            "type": {
                                # Missing field "parameter" here!
                                "unit": "permille"
                            },
                        }
                    ],
                },
                {
                    # Can't seem to get or create this instance from the database
                    "analysis_type": "Stable isotope analysis",
                    "session_index": 1,
                    "datum": [
                        {
                            "value": 0.2,
                            "error": 0.035,
                            "type": {"parameter": "delta 13C", "unit": "permille"},
                        }
                    ],
                },
            ],
        }

        res = client.put(
            "/api/v1/import-data/session", json={"filename": None, "data": data}
        )
        assert res.status_code == 400
        err = res.json["error"]

        assert err["type"] == "marshmallow.exceptions.ValidationError"
        # It could be useful to have a function that "unnests" these errors
        keypath = err["messages"]["analysis"]["0"]["datum"]["0"]["type"]["parameter"]
        assert keypath[0] == "Missing data for required field."

        # Make sure we don't partially import data
        res = db.session.query(db.model.sample).filter_by(name=new_name).first()
        assert res is None
