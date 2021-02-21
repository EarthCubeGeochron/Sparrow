from sparrow.util import relative_path
from pytest import mark
import gzip
import json


class TestSIMSImport:
    @mark.skip(reason="This hangs indefinitely")
    def test_large_sims_dataset(self, db):
        fn = relative_path(__file__, "fixtures", "2_20140602_d18O_KennyBefus.json.gz")
        with gzip.open(fn, "rb") as zipfile:
            data = json.loads(zipfile.read())
        db.load_data("session", data)
