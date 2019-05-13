from sparrow.import_helpers import BaseImporter
from json import dumps
import html

class IGSNImporter(BaseImporter):
    def import_data(self, all=True):
        q = self.db.session.query(self.db.model.igsn_data)
        for igsn_data in q:
            self.import_igsn(igsn_data)

    def import_igsn(self, model):
        data = model.data
        if not data: return
        s = data['sample']
        # Data with 'status' set are currently embargoed
        if 'status' in s: return
        v = dumps(s, indent=4, sort_keys=True)
        print(v)

        # Could set location precision from number of
        # decimal places in lat/lon string
        try:
            location = self.location(s['longitude'], s['latitude'])
        except KeyError:
            location = None


        igsn = s['igsn']
        name = html.unescape(s['name'])
        print(igsn, name)
        if not name:
            name = igsn

        sample = self.sample(
            igsn=igsn,
            defaults=dict(
                id=name
            ))

        self.db.session.add(sample)
        self.db.session.commit()
