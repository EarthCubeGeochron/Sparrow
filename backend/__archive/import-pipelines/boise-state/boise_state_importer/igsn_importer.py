from sparrow.import_helpers import BaseImporter
from json import dumps
from click import echo
import html


class IGSNImporter(BaseImporter):
    def import_data(self, all=True):
        q = self.db.session.query(self.db.model.igsn_data)
        self.num = 0
        for i, igsn_data in enumerate(q):
            self.import_igsn(igsn_data)
            print(igsn_data.igsn)
        echo(f"Imported {self.num} of {i+1} measurements")

    def import_igsn(self, model):
        data = model.data
        if not data:
            return
        s = data["sample"]
        # Data with 'status' set are currently embargoed
        if "status" in s:
            return
        self.num += 1
        v = dumps(s, indent=4, sort_keys=True)

        # Could set location precision from number of
        # decimal places in lat/lon string
        try:
            location = self.location(s["longitude"], s["latitude"])
        except KeyError:
            location = None

        igsn = s["igsn"]
        name = html.unescape(s["name"])
        sample = self.sample(igsn=igsn)
        sample.name = name
        sample.location = location
        sample.location_name = s.get(
            "primary_location_name", s.get("location_description", None)
        )

        self.db.session.add(sample)
        self.db.session.commit()
