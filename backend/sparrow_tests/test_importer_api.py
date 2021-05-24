from sqlalchemy import and_
from datetime import datetime
from pytest import mark
from .fixtures import basic_data, basic_d18O_data
from .helpers import json_fixture
import sys


class TestAPIImporter:
    def test_api_import(self, client,token):
        res = client.put("/api/v2/import-data/models/session", headers={"Authorization":token}, json={"filename": None, "data": basic_data})
        assert res.status_code == 200

    def test_basic_import(self, client, token):
        res = client.put("/api/v2/import-data/models/session", headers={"Authorization":token},json=basic_d18O_data)
        assert res.status_code == 200

    @mark.skip
    def test_complex_single_row_prior(self, client, db):
        # This test fails if before the overall import
        # Too much output
        # logging.disable(logging.CRITICAL)

        complex_data = json_fixture("large-test.json")
        complex_data["data"]["analysis"] = complex_data["data"]["analysis"][2:3]

        db.load_data("session", complex_data["data"])

    def test_complex_import(self, client, db):
        complex_data = json_fixture("large-test.json")
        db.load_data("session", complex_data["data"])

        a = db.model.analysis
        q = db.session.query(a).filter(and_(a.session_index is not None, a.analysis_type == "d18O measurement"))
        assert q.count() > 1

    def test_complex_single_row(self, client, db):
        # This test fails if before the overall import
        # Too much output
        # logging.disable(logging.CRITICAL)

        complex_data = json_fixture("large-test.json")
        complex_data["data"]["analysis"] = complex_data["data"]["analysis"][3:4]

        db.load_data("session", complex_data["data"])

    def test_very_large_import(self, client, token):

        import_size = 10

        i = 0
        analysis = []

        # while size < import_size:
        for i in range(import_size):
            item = {
                "analysis_type": "Stable isotope analysis",
                "session_index": i,
                "datum": [
                    {
                        "value": 0.2,
                        "error": 0.035,
                        "type": {"parameter": "delta 13C", "unit": "permille"},
                    }
                ],
            }
            i = i + 1
            analysis.append(item)
            size = sys.getsizeof(analysis)

        data = {
            "date": "2020-01-01T00:00:00",
            "name": "Session with existing instances",
            "sample": {"name": "LargeImport"},
            "analysis": analysis,
        }

        res = client.put("/api/v2/import-data/models/session",headers={"Authorization":token}, json={"filename": None, "data": data})
        assert res.status_code == 200

    def test_missing_field(self, client, db, token):
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

        res = client.put("/api/v2/import-data/models/session", headers={"Authorization":token},json={"filename": None, "data": data})
        assert res.status_code == 400
        err = res.json()["error"]

        assert err["type"] == "marshmallow.exceptions.ValidationError"
        # It could be useful to have a function that "unnests" these errors
        keypath = err["messages"]["analysis"]["0"]["datum"]["0"]["type"]["parameter"]
        assert keypath[0] == "Missing data for required field."

        # Make sure we don't partially import data
        res = db.session.query(db.model.sample).filter_by(name=new_name).first()
        assert res is None


class TestIsolation:
    def test_isolation(self, db):
        sessions = db.session.query(db.model.session).all()
        assert len(sessions) == 0


class TestDuplication:
    def test_duplicate_datum_import(self, client, db):
        """Seems like we are not importing data points that are the same between analyses..."""

        new_name = "Test error vvv"
        data = {
            "date": str(datetime.now()),
            "name": "Session with existing instances",
            "sample": {"name": new_name},
            "analysis": [
                {
                    "analysis_type": "Stable isotope analysis",
                    "session_index": 0,
                    "datum": [
                        {
                            "value": 0.1,
                            "error": 0.025,
                            "type": {"parameter": "delta 13C", "unit": "permille"},
                        }
                    ],
                },
                {
                    "analysis_type": "Stable isotope analysis",
                    "session_index": 1,
                    "datum": [
                        {
                            "value": 0.1,
                            "error": 0.025,
                            "type": {"parameter": "delta 13C", "unit": "permille"},
                        }
                    ],
                },
            ],
        }

        # Two datum with unique analysis numbers should be created, but are not.
        res = db.load_data("session", data)
        assert len(res.analysis_collection) == 2
        for a in res.analysis_collection:
            assert len(a.datum_collection) == 1
        assert len(db.session.query(db.model.datum).all()) == 2

class TestSampleChange:
    def test_sample_name_change(self, client, db):
        """Change name of sample in database"""

        combined_name = "WI-STD-74"

        data = {
                "date": str(datetime.now()),
                "name": "Session1",
                "sample": {"name": "WI-STD-74 B"}
                }

        db.load_data("session", data)

        data = {
                "date": str(datetime.now()),
                "name": "Session2",
                "sample": {"name": "WI-STD-74 C"}
                }

        db.load_data("session", data)

        data = {
                "date": str(datetime.now()),
                "name": "Session2",
                "sample": {"name": "WI-STD-12"}
                }
        db.load_data("session", data)

        existing = db.session.query(Sample).get(ele["name"])

        # Somewhere here need to do the combination of Sample 1 and 2 into single sample...

        # Two datum with unique analysis numbers should be created, but are not.
        res = db.load_data("session", data)
        # assert 1==0
        # I think looking for 2 samples is the easiest way to check given the DB currently keeps unique keys.
        assert len(db.session.query(db.model.Sample).all()) == 2
