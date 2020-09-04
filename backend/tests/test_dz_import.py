from sparrow.util import relative_path
from sparrow.interface import model_interface
from sparrow.ext.detrital_zircon import DetritalZirconTableImporter
from pandas import read_csv
from pytest import mark, fixture


def import_dz_test_data():
    importer = DetritalZirconTableImporter()
    fn = relative_path(__file__, "fixtures", "detrital-zircon-F-90.csv")
    df = read_csv(fn)
    return importer(df)


@fixture(scope="module")
def dz_data():
    yield import_dz_test_data()


@mark.slow
def test_dz_import(db, dz_data):
    """Importing ~300 DZ measurements is slow"""
    db.load_data("session", dz_data)


@mark.xfail(reason="This doesn't work for some reason.")
def test_dz_import_iterative(db, dz_data):
    """A potentially quicker method to add analyses after creation"""
    analysis_list = dz_data.pop("analysis")

    _session = model_interface(db.model.session, session=db.session)()
    _analysis = model_interface(db.model.analysis, session=db.session)()

    with db.session.no_autoflush:
        session = _session.load(dz_data, session=db.session)
        for a in analysis_list:
            a1 = _analysis.load(a, session=db.session, partial=True)
            session.analysis_collection.append(a1)
        db.session.add(session)
        db.session.commit()
