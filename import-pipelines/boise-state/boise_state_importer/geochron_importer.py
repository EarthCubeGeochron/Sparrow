from lxml.etree import tostring
from itertools import chain

def text(et, key):
    v = et.findtext(key)
    if v == '': return None
    return v

class GeochronImporter(object):
    """
    A basic Sparrow importer for Geochron.org XML
    """
    def __init__(self, db):
        self.db = db
        self.models = self.db.mapped_classes

    def import_datafile(self, et):
        """
        Aliquot -> analysis_session
        """
        session = self.models.session()
        fractions = et.find("analysisFractions")

        analysis_collection = []
        for i,f in enumerate(fractions):
            v = self.import_analysis(f, session_index=i, analysis_type="analysisFraction")
            analysis_collection.append(v)

        analysis_collection.append(self.import_dates(et.find("sampleDateModels")))

        session.analysis_collection = analysis_collection

        # Set publication
        ref = text(et, "aliquotReference")
        if ref: session.publication = self.publication(ref)

        # Set IGSN
        igsn = text(et, "aliquotIGSN")
        if str(igsn) == '0': igsn = None
        session.igsn = igsn

        dates = [i.text for i in et.findall('.//dateCertified')]
        date = max(set(dates), key=dates.count)
        session.date = date

        igsn = text(et, "sampleIGSN")
        if str(igsn) == '0': igsn = None
        name = text(et, "aliquotName")
        if igsn or name:
            session.sample = self.sample(id=name, igsn=igsn)

        self.db.session.add(session)

    def sample(self, **kwargs):
        self.db.get_or_create(self.models.sample, **kwargs)

    def publication(self, doi, title=None):
        return self.db.get_or_create(
            self.models.publication,
            doi=doi, defaults=dict(title=title))

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
        analysis.datum_collection = values
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

    def error_metric(self, id):
        return self.db.get_or_create(
            self.models.error_metric,
            id=id, authority="Boise State")

    def parameter(self, id):
        return self.db.get_or_create(
            self.models.parameter,
            id=id, authority="Boise State")

    def datum_type(self, et, unit='unknown'):
        error_metric = self.error_metric(et.find('uncertaintyType').text)
        # Error values are *assumed* to be at the 1s level, apparently
        parameter = self.parameter(et.find('name').text)

        return self.db.get_or_create(
            self.models.datum_type,
            parameter=parameter.id,
            error_metric=error_metric.id,
            unit=unit)

    def import_datum(self, et):
        """
        ValueModel -> datum
        """
        v = et.find('value').text
        if not v: return None
        datum = self.models.datum(
            value=v,
            error=et.find('oneSigma').text)
        datum.datum_type=self.datum_type(et)
        return datum
