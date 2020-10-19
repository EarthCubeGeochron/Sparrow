from .helpers import json_fixture
from sparrow.ext.pychron import PyChronJSONImporter
from pytest import mark


class TestPyChronJSONImporter(PyChronJSONImporter):
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
        data = TestPyChronJSONImporter().import_file(ia, filename=None)
        res = db.load_data("session", data)
        check_age_units(res, "dimensionless")

    # @mark.xfail(reason="We don't handle updating data  well at the moment.")
    def test_pychron_import(self, db):
        ia = json_fixture("pychron-interpreted-age.json")
        assert ia is not None
        data = PyChronJSONImporter().import_file(ia, filename=None)
        res = db.load_data("session", data)
        check_age_units(res, "Ma")
