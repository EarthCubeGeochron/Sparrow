from sparrow.util import relative_path
from pandas import read_csv


class DetritalZirconTableImporter:
    keys = [
        "analysis",
        "uranium_ppm",
        "ratio_206Pb_204Pb",
        "ratio_U_Th",
        "ratio_206Pb_207Pb",
        "ratio_206Pb_207Pb_err",
        "ratio_207Pb_235U",
        "ratio_207Pb_235U_err",
        "ratio_206Pb_238U",
        "ratio_206Pb_238U_err",
        "error_corr",
        "age_206Pb_238U",
        "age_206Pb_238U_err",
        "age_207Pb_235U",
        "age_207Pb_235U_err",
        "age_206Pb_207Pb",
        "age_206Pb_207Pb_err",
        "best_age",
        "best_age_err",
        "concordia",
    ]

    def unit_for(self, key):
        if key.startswith("age"):
            return "Ma"
        if key.startswith("ratio"):
            return "ratio"
        if key.endswith("ppm"):
            return "ppm"
        return "dimensionless"

    def translate_datum(self, row, key):
        if key == "analysis" or key.endswith("_err"):
            return None
        return {
            "value": row[key],
            "error": row.get(key + "_err", None),
            "type": {"parameter": key, "unit": self.unit_for(key)},
        }

    def translate_analysis(self, ix, row):
        data_vals = [self.translate_datum(row, field) for field in self.keys]
        return {
            "analysis_name": row.get("analysis"),
            "datum": [v for v in data_vals if v is not None],
            "session_index": int(ix),
        }

    def __call__(self, df):
        sample_id = df.groupby("sample").first().index[0]
        analyses = [self.translate_analysis(ix, row) for ix, row in df.iterrows()]
        return {
            "sample": {"name": sample_id},
            "analysis": analyses,
            "date": "2017-06-07T00:00:00",
        }


def test_dz_import(db):
    fn = relative_path(__file__, "fixtures", "detrital-zircon-F-90.csv")
    df = read_csv(fn)

    importer = DetritalZirconTableImporter()
    res = importer(df)
    db.load_data("session", res)

    assert len(df) > 100
