from sparrow.util import relative_path
from pandas import read_csv


def test_dz_import(db):
    fn = relative_path(__file__, "fixtures", "detrital-zircon-F-90.csv")
    df = read_csv(fn)
    assert len(df) > 100
