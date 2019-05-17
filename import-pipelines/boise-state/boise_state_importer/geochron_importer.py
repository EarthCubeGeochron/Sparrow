from lxml.etree import tostring
from itertools import chain
from sparrow.import_helpers import BaseImporter
from datetime import datetime

def text(et, key):
    v = et.findtext(key)
    if v == '': return None
    return v

class GeochronImporter(BaseImporter):
    """
    A basic Sparrow importer for Geochron.org XML
    """
    authority = "Boise State"

    def import_datafile(self, et):
        """
        Aliquot -> session
        """
        dates = [i.text for i in et.findall('.//dateCertified')]
        date = max(set(dates), key=dates.count)
        if not date:
            date = datetime.min()

        session = self.models.session(date=date)

        # Set publication
        ref = text(et, "aliquotReference")
        if ref: session._publication = self.publication(ref)

        # Set IGSN
        igsn = text(et, "aliquotIGSN")
        if str(igsn) == '0': igsn = None
        session.igsn = igsn

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
