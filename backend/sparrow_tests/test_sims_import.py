from sparrow.util import relative_path
import gzip
import json


class TestSIMSImport:
    def test_large_sims_dataset(self, db):
        fn = relative_path(__file__, "fixtures", "2_20140602_d18O_KennyBefus.json.gz")
        with gzip.open(fn, "rb") as zipfile:
            data = json.loads(zipfile.read())
        db.load_data("session", data)
