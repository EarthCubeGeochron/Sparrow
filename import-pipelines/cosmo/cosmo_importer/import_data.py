from pandas import read_excel
from datetime import datetime
from sparrow.import_helpers import BaseImporter

class CosmoImporter(BaseImporter):
    authority = "Cosmo Lab"
    def import_row(self, row):
        """
        The cosmo case is kinda weird because there tends to be one
        analysis -> session -> sample
        for each measurement, so it is unclear where to put various
        data points. For instance, elevation could be a sample parameter
        or analysis parameter.
        """
        sample = self.sample(name=row.loc['index'])
        lon = row.loc['Long (DD)']
        lat = row.loc['Lat (DD)']
        sample.location = self.location(lon, lat)
        sample.elevation=row.loc['Elev (m)']

        session = self.models.session()
        nuclide = row.loc['Nuclide']

        session.technique = self.method(f"{nuclide} cosmogenic nuclide dating").id
        session.material = self.material(row.loc['Min Phase']).id
        session.date = datetime(year=row.loc['Collection Date'], month=1, day=1)
        session.sample_id = sample.id

        self.db.session.add(session)

        self.measured_parameters(session, row)
        self.model_output(session, row)

        self.db.session.commit()


    def measured_parameters(self, session, row):
        nuclide = row.loc['Nuclide']

        analysis = self.models.analysis(
            analysis_type='Sample measurements',
            is_interpreted=False)

        analysis.material = self.material(nuclide).id

        dc = []
        v = row.loc['Thickness (cm)']
        val = self.datum(analysis, "Thickness", v, unit='cm')
        dc.append(val)

        v = row.loc['Density (g/cm^3)']
        val = self.datum(analysis,"Density", v, unit='g/cm^3')
        dc.append(val)

        v = row.loc['Shielding']
        val = self.datum(analysis,"Shielding", v)
        dc.append(val)

        v = row.loc['Erosion']
        val = self.datum(analysis,"Erosion", v)
        dc.append(val)

        v = row.loc['Be-concent']
        e = row.loc['Be-concent error']
        val = self.datum(analysis, 'Be-concent', v, error=e, unit='concentration')
        dc.append(val)

        analysis._session = session
        return analysis

    def model_output(self, session, row):
        nuclide = row.loc['Nuclide']

        analysis = self.models.analysis(
            analysis_type='CRONUS model output',
            is_interpreted=True)
        analysis.material = self.material(nuclide).id
        for k in ['St', 'Lm', 'LSDn']:
            v = row.loc[k+'_Age']
            e = row.loc[k+'_Exterr']
            d = self.datum(analysis, k+"_Age", v,
                error=e, unit='yr',
                error_metric='absolute',
                is_computed=True,
                is_interpreted=True)
            # Special row for interror
            d.interror = row.loc[k+'_Interr']
        analysis._session = session
        self.db.session.add(analysis)
        return analysis

def import_datafile(db, fn):

    input = read_excel(fn, sheet_name=0, index_col=0, header=0)
    output = read_excel(fn, sheet_name=1, index_col=0, header=0)

    df = input.join(output, rsuffix="out").reset_index()

    importer = CosmoImporter(db)
    for ix, row in df.iterrows():
        importer.import_row(row)

    return True
