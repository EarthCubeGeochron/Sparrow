from .helpers import json_fixture
from sparrow.ext.pychron import PyChronJSONImporter
from rich import print


def test_pychron_import(db):
    ia = json_fixture("pychron-interpreted-age.json")
    assert ia is not None
    data = PyChronJSONImporter().import_file(ia)
    db.load_data("session", data)
