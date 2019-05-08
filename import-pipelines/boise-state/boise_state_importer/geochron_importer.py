from lxml.etree import tostring

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
        session.analysis_collection = [
            self.import_analysis(f) for f in fractions]
        self.db.session.add(session)

    def import_analysis(self, et):
        """
        AnalysisFraction -> analysis
        """
        am = et.find("analysisMeasures")
        vm = am.findall("ValueModel")

        analysis = self.models.analysis()

        analysis.datum_collection = [
            self.import_datum(f)
            for f in am.findall("ValueModel")]

        return analysis

    def error_metric(self, id):
        return self.db.get_or_create(
            self.models.error_metric,
            id=id, authority="Boise State")

    def parameter(self, id):
        return self.db.get_or_create(
            self.models.parameter,
            id=id, authority="Boise State")

    def datum_type(self, et):
        error_metric = self.error_metric(et.find('uncertaintyType').text)
        # Error values are *assumed* to be at the 1s level, apparently
        parameter = self.parameter(et.find('name').text)

        return self.db.get_or_create(
            self.models.datum_type,
            parameter=parameter.id,
            error_metric=error_metric.id,
            unit='unknown')

    def import_datum(self, et):
        """
        ValueModel -> datum
        """
        datum = self.models.datum(
            value=et.find('value').text,
            error=et.find('oneSigma').text)
        datum.datum_type=self.datum_type(et)
        return datum
