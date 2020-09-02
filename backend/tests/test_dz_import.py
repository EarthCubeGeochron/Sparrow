from sparrow.util import relative_path
from sparrow.ext.detrital_zircon import DetritalZirconTableImporter
from pandas import read_csv
from pytest import mark, fixture


@fixture(scope="module")
def dz_data():
    """Importing ~300 DZ measurements is slow"""
    importer = DetritalZirconTableImporter()
    fn = relative_path(__file__, "fixtures", "detrital-zircon-F-90.csv")
    df = read_csv(fn)
    yield importer(df)


@mark.slow
def test_dz_import(db, dz_data):
    db.load_data("session", dz_data)


@mark.xfail(reason="This doesn't work yet.")
def test_dz_import_iterative(db, dz_data):
    """A potentially quicker method to add analyses after creation"""
    analysis_list = dz_data.pop("analysis")

    session = db.load_data("session", dz_data)
    assert session.id is not None

    for a in analysis_list:
        db.load_data("analysis", dict(session=session.id, **a))
