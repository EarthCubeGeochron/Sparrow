from rich import print
from datetime import datetime


class PyChronJSONImporter:
    """Basic transformation class for PyChron data files"""

    def __init__(self):
        pass

    def transform_datum(self, analysis, key):
        v = analysis.pop(key)
        e = analysis.pop(key + "_err", None)
        if v == 0 and e == 0:
            return None
        return {
            "value": v,
            "error": e,
            "type": key,
        }

    def transform_analysis(self, analysis):
        data = []
        for k in ["age", "kca", "kcl", "radiogenic_yield"]:
            data.append(self.transform_datum(analysis, k))
        return {"name": analysis.pop("record_id"), "data": data}

    def transform_sample(self, sample):
        lat = sample.get("latitude")
        lon = sample.get("longitude")
        location = None
        if lat != 0 and lon != 0:
            location = {"type": "Point", "coordinates": [lon, lat]}

        res = {"name": sample["sample"], "location": location}

        return res

    def transform_ages(self, ages):
        datum = []
        for age in ["integrated", "isochron", "plateau", "weighted"]:
            d = self.transform_datum(ages, age + "_age")
            if d is not None:
                datum.append(d)
        return {"datum": datum, "type": "Ages"}

    def import_file(self, data):
        analyses = [self.transform_analysis(a) for a in data["analyses"]]
        analyses.append(self.transform_ages(data["preferred"]["ages"]))

        res = {"analysis": analyses}

        # Copy a few fields directly:
        for k in ["name", "uuid"]:
            res[k] = data[k]

        # There is no _DATE_ in the IA file!
        res["date"] = datetime.min

        res["sample"] = self.transform_sample(data["sample_metadata"])

        return res
