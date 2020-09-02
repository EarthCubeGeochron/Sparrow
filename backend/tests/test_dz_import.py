from sparrow.util import relative_path
from sparrow.ext.detrital_zircon import DetritalZirconTableImporter
from pandas import read_csv
from pytest import mark


@mark.slow
def test_dz_import(db):
    fn = relative_path(__file__, "fixtures", "detrital-zircon-F-90.csv")
    df = read_csv(fn)

    importer = DetritalZirconTableImporter()
    res = importer(df)
    db.load_data("session", res)
