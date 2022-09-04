from sparrow.import_helpers import BaseImporter
from sparrow.util import relative_path
from pandas import read_csv


class IsotopeImporter(BaseImporter):
    def import_all(self):
        df = relative_path(__file__, "fixtures", "simple-carbon-oxygen-isotopes.csv")
        self.iterfiles([df])

    def import_datafile(self, fn, rec, **kwargs):
        df = read_csv(fn)

        for ix, row in df.iterrows():
            data = {
                "name": f"Sample {row.height:.2f}",
                "session": [
                    {
                        "technique": "Stable isotope measurements",
                        "date": "1900-01-01 00:00:00+00",
                        "analysis": [
                            {
                                "analysis_type": "Stable isotope measurements",
                                "datum": [
                                    {
                                        "value": row.delta13c,
                                        "error": row.delta13c_error,
                                        "type": {
                                            "parameter": "delta13c",
                                            "unit": "permille",
                                        },
                                    },
                                    {
                                        "value": row.delta18o,
                                        "error": row.delta18o_error,
                                        "type": {
                                            "parameter": "delta18o",
                                            "unit": "permille",
                                        },
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
            self.db.load_data("sample", data, strict=True)


class TestDataFileImport:
    def test_import_datafile(self, app):
        importer = IsotopeImporter(app)
        importer.import_all()

    def test_import_again(self, app, db):
        importer = IsotopeImporter(app)
        importer.import_all()

        n_files = db.session.query(db.model.data_file).count()
        assert n_files == 1

    def test_import_again_again(self, app, db):
        importer = IsotopeImporter(app)
        importer.import_all()

        n_files = db.session.query(db.model.data_file).count()
        assert n_files == 1
