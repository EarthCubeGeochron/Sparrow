from lxml.etree import tostring
from itertools import chain
from sparrow.import_helpers import BaseImporter, SparrowImportError
from datetime import datetime

def extract_table(csv_data):
    tbl = csv_data
    if tbl is None:
        return
    f = StringIO()
    f.write(tbl.decode())
    f.seek(0)
    df = read_csv(f)
    df = df.iloc[:,1:]
    return extract_data(df)

def infer_project_name(fp):
    folders = fp.split("/")[:-1]
    return max(folders, key=len)

class LaserchronImporter(BaseImporter):
    """
    A basic Sparrow importer for cleaned ETAgeCalc and NUPM AgeCalc files.
    """
    authority = "ALC"

    def import_all(self):
        q = self.db.session.query(self.db.model.data_file)
        self.iterfiles(q)

    def import_datafile(self, rec):
        """
        data file -> sample(s)
        """
        if "NUPM-MON" in rec.basename:
            raise SparrowImportError("NUPM-MON files are not handled yet")
        if not rec.csv_data:
            raise SparrowImportError("CSV data not extracted")
        data, meta = extract_table(rec.csv_data)
        project = infer_project_name(rec.file_path)

        return False


    def import_session(self, df, date):
        date = rec.file_mtime or datetime.min()
        session = self.models.session(date=date)
        # Add this to our data file model
        rec._session = session

        # Import analysis sessions
        igsn = text(et, "sampleIGSN")
        if str(igsn) == '0': igsn = None
        name = text(et, "aliquotName")
        if igsn or name:
            session._sample = self.sample(id=name, igsn=igsn)

        fractions = et.find("analysisFractions")

        for i,f in enumerate(fractions):
            s = self.import_analysis(f, session_index=i, analysis_type="analysisFraction")
            s._session = session
            self.db.session.add(s)

        s1 = self.import_dates(et.find("sampleDateModels"))
        s1._session = session
        self.db.session.add(s1)

        self.db.session.add(session)

    def import_dates(self, et):
        """
        SampleDateModel -> analysis(interpreted: true)
        """
        models = et.findall("SampleDateModel")

        # Need to specify unit somehow
        values = [self.import_datum(f) for f in models]

        analysis = self.models.analysis(
            is_interpreted=True,
            is_standard=False,
            analysis_type="Interpreted Age")
        analysis.datum_collection = [v for v in values if v is not None]
        return analysis

    def import_analysis(self, et, **kwargs):
        """
        AnalysisFraction -> analysis
        """
        def data_iterator(et, key, unit, model="ValueModel"):
            return (self.import_datum(f)
                for f in et.find(key).findall(model))

        values = chain(
            data_iterator(et, 'analysisMeasures', 'unknown'),
            data_iterator(et, "measuredRatios", 'ratio_measured', model='MeasuredRatioModel'),
            data_iterator(et, "radiogenicIsotopeRatios", 'ratio_radiogenic'))

        analysis = self.models.analysis(**kwargs)

        analysis.datum_collection = [d for d in values if d is not None]
        return analysis

    def import_datum(self, et):
        """
        ValueModel -> datum
        """
        parameter = et.find('name').text
        try:
            value = et.find('value').text
            assert float(value) is not None
        except:
            return None


        return self.datum(parameter, value,
            error=text(et, 'oneSigma'),
            error_metric=text(et, 'uncertaintyType'))
