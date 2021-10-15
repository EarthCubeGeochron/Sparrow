from .helpers import json_fixture
from sparrow.ext.pychron import PyChronJSONImporter
from pytest import mark
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation


class PyChronJSONImporterTest(PyChronJSONImporter):
    """A PyChron importer that phones it in on units. This helps to assess
    whether we can successfully overwrite to the proper units for successive imports.
    It is important for progressive enhancement of the web application."""

    def datum_type_for(self, key):
        # Right now we phone this in with "dimensionless" for everything
        return {"unit": "dimensionless", "parameter": key}


def check_age_units(session, unit):
    """Make sure ages tracked by the importer are recorded with the proper units"""
    for analysis in session.analysis_collection:
        if analysis.analysis_name != "Ages":
            continue
        for datum in analysis.datum_collection:
            if not datum._datum_type._parameter.id.endswith("_age"):
                continue
            assert datum._datum_type._unit.id == unit


class TestPyChronImport:
    def test_pychron_poor_quality_import(self, db):
        ia = json_fixture("pychron-interpreted-age.json")
        assert ia is not None
        data = PyChronJSONImporterTest().import_file(ia, filename=None)
        res = db.load_data("session", data)
        check_age_units(res, "dimensionless")

    @mark.xfail(reason="We don't handle updating data well at the moment.")
    def test_pychron_import(self, db):
        ia = json_fixture("pychron-interpreted-age.json")
        assert ia is not None
        data = PyChronJSONImporter().import_file(ia, filename=None)
        res = db.load_data("session", data)
        check_age_units(res, "Ma")


class TestPychronIASessionImport:
    def test_session_import(self, db):
        """Test that non-conforming session import fails with a meaningful error message."""
        ia = json_fixture("pychron-failing-session.json")
        try:
            db.load_data("session", ia)
            assert False
        except IntegrityError as err:
            assert isinstance(err.orig, UniqueViolation)

    def test_session_import_fixed(self, db):
        """Fix session import by getting rid of non-conforming analyses."""
        ia = json_fixture("pychron-failing-session.json")
        ia["analysis"] = [
            i for i in ia["analysis"] if i["analysis_type"] != "Preferred"
        ]
        db.load_data("session", ia)
        # check_age_units(res, "Ma")
