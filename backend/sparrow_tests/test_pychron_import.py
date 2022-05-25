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


sample_data = {
    'member_of': {'name': 'JT7', 'material': 'rock'},
    'researcher': [{'name': 'Martin'}],
    'laboratory': 'Martin',
    'name': 'JT7_a02',
    'material': 'Apatite',
    'lab_id': '21-00001',
    'from_archive': 'false',
    'session': [
        {
            'technique': {'id': 'Picking Information'},
            'instrument': {'name': 'Leica microscope'},
            'date': '2021-04-09 00:00:00',
            'analysis': [
                {
                    'analysis_type': 'Grain Shape',
                    'datum': [
                        {'value': 167.2, 'error': None, 'type': {'parameter': 'Length 1', 'unit': 'μm'}},
                        {'value': 85.3, 'error': None, 'type': {'parameter': 'Width 1', 'unit': 'μm'}},
                        {'value': 158.2, 'error': None, 'type': {'parameter': 'Length 2', 'unit': 'μm'}},
                        {'value': 60.0, 'error': None, 'type': {'parameter': 'Width 2', 'unit': 'μm'}}
                    ],
                    'attribute': [
                        {'parameter': 'Geometry', 'value': '4.0'},
                        {'parameter': 'Crystal terminations', 'value': '1.0'}
                    ]
                },
                {
                    'analysis_type': 'Grain Characteristics',
                    'attribute': [
                        {'parameter': 'Color', 'value': 'purple with orange at outside'},
                        {'parameter': 'Surface color/staining', 'value': 'none'},
                        {'parameter': 'Roughness (1-3)', 'value': '4.0'},
                        {'parameter': 'Idealness of Crystal (A-C)', 'value': 'B'},
                        {'parameter': 'Mineral inclusions', 'value': 'none'},
                        {'parameter': 'Fluid inclusions', 'value': 'none'},
                        {'parameter': 'Notes', 'value': 'very rough grain but overall shape is still visible'}
                    ]
                }
            ]
        },
        {
            'technique': {'id': 'Dates and other derived data'},
            'date': '1900-01-01 00:00:00+00',
            'analysis': [
                {
                    'analysis_type': 'Alpha ejection correction values',
                    'datum': [
                        {'value': 0.6321567005645838, 'error': 0.0, 'type': {'parameter': '238U Ft', 'unit': ''}},
                        {'value': 0.5797092776813073, 'error': 0.0, 'type': {'parameter': '235U Ft', 'unit': ''}},
                        {'value': 0.5719712571439586, 'error': 0.0, 'type': {'parameter': '232Th Ft', 'unit': ''}},
                        {'value': 0.8774698568240697, 'error': 0.0, 'type': {'parameter': '147Sm Ft', 'unit': ''}}
                    ]
                },
                {
                    'analysis_type': 'Rs, mass, concentrations',
                    'datum': [
                        {
                            'value': 1.369728055938351,
                            'error': 0.0,
                            'type': {'parameter': 'Dimensional mass', 'unit': 'μg'}
                        },
                        {
                            'value': 35.51461146658557,
                            'error': 0.0,
                            'type': {'parameter': 'Equivalent Spherical Radius', 'unit': 'μm'}
                        }
                    ]
                }
            ]
        }
    ]
}


def test_session_import(db):
    db.load_data("sample", sample_data)
