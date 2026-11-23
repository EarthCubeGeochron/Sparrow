from datetime import datetime
from os import path

from sparrow.core.util import run
from sparrow.pipelines import Analysis, Datum, DatumType, Point, Sample, Session


class PyChronJSONImporter:
    """Builds a session from a PyChron interpreted age (IA) file."""

    def datum_type_for(self, key) -> DatumType:
        if key == "age":
            # We should be more specific about step ages
            key = "step_age"
        if key.endswith("age"):
            return DatumType(unit="Ma", parameter=key)
        return DatumType(unit="unknown", parameter=key)

    def transform_datum(self, analysis, key):
        v = analysis.pop(key)
        e = analysis.pop(key + "_err", None)
        if v == 0 and e == 0:
            return None
        return Datum(value=v, error=e, type=self.datum_type_for(key))

    def transform_analysis(self, analysis, index=None) -> Analysis:
        data = [
            self.transform_datum(analysis, k)
            for k in ["age", "kca", "kcl", "radiogenic_yield"]
        ]
        # TODO: allow UUIDs to be created in Analysis model aswell.
        return Analysis(
            analysis_type="Heating step",
            analysis_name=analysis.pop("record_id"),
            datum=[d for d in data if d is not None],
            data={"in_plateau": analysis.pop("plateau_step")},
            session_index=index,
        )

    def transform_sample(self, sample) -> Sample:
        lat = sample.get("latitude")
        lon = sample.get("longitude")
        location = None
        if lat != 0 and lon != 0:
            try:
                location = Point(coordinates=(float(lon), float(lat)))
            except (TypeError, ValueError):
                pass
        return Sample(name=sample["sample"], location=location)

    def transform_ages(self, ages) -> Analysis:
        datum = []
        for age in ["integrated", "isochron", "plateau", "weighted"]:
            d = self.transform_datum(ages, age + "_age")
            if d is not None:
                datum.append(d)
        return Analysis(datum=datum, analysis_name="Ages")

    def get_commit_date(self, fn):
        # There is no date in the IA file, so we use the commit date
        # as a proxy.
        DT_FMT = "%Y-%m-%d %H:%M:%S"
        ret = run(
            "git log -1",
            '--format="%ad"',
            f'--date=format:"{DT_FMT}"',
            "--",
            fn,
            capture_output=True,
            check=True,
            cwd=path.dirname(fn),
        )

        date = ret.stdout.decode("utf-8").strip()
        return datetime.strptime(date, DT_FMT)

    def build_session(self, data, filename=None) -> Session:
        analyses = [
            self.transform_analysis(a, index=i) for i, a in enumerate(data["analyses"])
        ]
        analyses.append(self.transform_ages(data["preferred"]["ages"]))

        date = datetime.min
        if filename is not None:
            date = self.get_commit_date(filename)

        # NOTE: I am unsure if we should hijack Sparrow's internal UUID field for PyChron
        # ids, or create a new field for this in the PyChron Importer Plugin. I lean towards
        # the former.
        return Session(
            name=str(data["name"]),
            uuid=str(data["uuid"]),
            date=date,
            sample=self.transform_sample(data["sample_metadata"]),
            analysis=analyses,
        )

    def import_file(self, data, filename=None) -> dict:
        """Nested data for a PyChron IA file, as the import API takes it."""
        return self.build_session(data, filename=filename).to_import_data()
