import subprocess

from rich import print
from datetime import datetime


class PyChronJSONImporter:
    """Basic transformation class for PyChron interpreted age data files"""

    def __init__(self):
        pass

    def datum_type_for(self, key):
        # Right now we phone this in with "dimensionless" for everything
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

    def transform_analysis(self, analysis):
        data = []
        for k in ["age", "kca", "kcl", "radiogenic_yield"]:
            data.append(self.transform_datum(analysis, k))
        # TODO: allow UUIDs to be created in Analysis model aswell.
        return {
            "analysis_name": analysis.pop("record_id"),
            "datum": data,
            "analysis_type": "Heating step",
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

    def import_file(self, fn, data):
        """Build basic nested JSON representation of a PyChron IA file."""
        analyses = [self.transform_analysis(a) for a in data["analyses"]]
        analyses.append(self.transform_ages(data["preferred"]["ages"]))
        print(analyses)

        res = {"analysis": analyses}

        # Copy a few fields directly:
        # NOTE: I am unsure if we should hijack Sparrow's internal UUID field for PyChron
        # ids, or create a new field for this in the PyChron Importer Plugin. I lean towards
        # the former.
        for k in ["name", "uuid"]:
            res[k] = str(data[k])

        # There is no _DATE_ in the IA file!
#        res["date"] = datetime.min.isoformat()

        # extract date from commit
        DT_FMT ='%Y-%m-%d %H:%M:%S'
        ret = subprocess.check_output(
            ['git', 'log', '-1', '--format="%ad"', '--date=format:{}'.format(DT_FMT), '--', fn])

        date = ret.decode('utf8').strip()[1:-1]
        date = datetime.strptime(date, DT_FMT)
        ret['date'] = date.isoformat()

        res["sample"] = self.transform_sample(data["sample_metadata"])

        return res
