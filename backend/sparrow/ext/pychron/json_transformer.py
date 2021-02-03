from os import path
from datetime import datetime
from sparrow.util import run


class PyChronJSONImporter:
    """Basic transformation class for PyChron interpreted age data files
    to nested JSON.
    """

    def __init__(self):
        pass

    def datum_type_for(self, key):
        if key == "age":
            # We should be more specific about step ages
            key = "step_age"
        if key.endswith("age"):
            return {"unit": "Ma", "parameter": key}
        return {"unit": "unknown", "parameter": key}

    def transform_datum(self, analysis, key):
        v = analysis.pop(key)
        e = analysis.pop(key + "_err", None)
        if v == 0 and e == 0:
            return None
        return {
            "value": v,
            "error": e,
            "type": self.datum_type_for(key),
        }

    def transform_analysis(self, analysis, index=None):
        data = []
        for k in ["age", "kca", "kcl", "radiogenic_yield"]:
            data.append(self.transform_datum(analysis, k))
        # TODO: allow UUIDs to be created in Analysis model aswell.
        return {
            "analysis_type": "Heating step",
            "analysis_name": analysis.pop("record_id"),
            "datum": data,
            "in_plateau": analysis.pop("plateau_step"),
            "session_index": index,
        }

    def transform_sample(self, sample):
        lat = sample.get("latitude")
        lon = sample.get("longitude")
        location = None
        if lat != 0 and lon != 0:
            try:
                location = {"type": "Point", "coordinates": [float(lon), float(lat)]}
            except (TypeError, ValueError):
                pass

        res = {"name": sample["sample"], "location": location}

        return res

    def transform_ages(self, ages):
        datum = []
        for age in ["integrated", "isochron", "plateau", "weighted"]:
            d = self.transform_datum(ages, age + "_age")
            if d is not None:
                datum.append(d)
        return {"datum": datum, "analysis_name": "Ages"}

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

    def import_file(self, data, filename=None):
        """Build basic nested JSON representation of a PyChron IA file."""
        analyses = [
            self.transform_analysis(a, index=i) for i, a in enumerate(data["analyses"])
        ]
        analyses.append(self.transform_ages(data["preferred"]["ages"]))

        res = {"analysis": analyses}

        # Copy a few fields directly:
        # NOTE: I am unsure if we should hijack Sparrow's internal UUID field for PyChron
        # ids, or create a new field for this in the PyChron Importer Plugin. I lean towards
        # the former.
        for k in ["name", "uuid"]:
            res[k] = str(data[k])

        if filename is not None:
            res["date"] = self.get_commit_date(filename).isoformat()
        else:
            res["date"] = datetime.min.isoformat()

        res["sample"] = self.transform_sample(data["sample_metadata"])

        return res
