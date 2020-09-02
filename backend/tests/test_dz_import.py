from sparrow.util import relative_path
from sparrow.ext.detrital_zircon import DetritalZirconTableImporter
from pandas import read_csv
from pytest import mark
from rich import print


@mark.slow
def test_dz_import(db):
    fn = relative_path(__file__, "fixtures", "detrital-zircon-F-90.csv")
    df = read_csv(fn)

    importer = DetritalZirconTableImporter()
    res = importer(df)

    analysis_list = res.pop("analysis")

    session = db.load_data("session", res)
    assert session.id is not None

    for a in analysis_list:
        db.load_data("analysis", dict(session=session.id, **a))
