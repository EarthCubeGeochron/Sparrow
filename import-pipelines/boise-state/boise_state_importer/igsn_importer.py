from sparrow.import_helpers import BaseImporter

class IGSNImporter(BaseImporter):
    def import_data(self, all=True):
        q = self.db.session.query(self.db.model.igsn_data)
        for igsn_data in q:
            self.import_igsn(igsn_data)

    def import_igsn(self, model):
        data = model.data
        if not data: return
        data = data['sample']
        if 'status' in data: return
        print(data)
