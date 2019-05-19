"""
Import script for *ET-Redux* xml-formatted data
from Boise State Geochronology Laboratory
"""
from lxml.etree import tostring, XML, QName
from click import echo
from itertools import chain
from sparrow.import_helpers import BaseImporter, SparrowImportError
from datetime import datetime
from sqlalchemy.exc import DataError

def text(et, key):
    v = et.findtext(key)
    if v == '': return None
    return v

def strip_ns_prefix(tree):
    #xpath query for selecting all element nodes in namespace
    query = "descendant-or-self::*[namespace-uri()!='']"
    #for each element returned by the above xpath query...
    for element in tree.xpath(query):
        #replace element name with its local name
        element.tag = QName(element).localname
    return tree

class ETReduxImporter(BaseImporter):
    """
    A Sparrow importer for Geochron.org ETRedux XML
    """
    authority = "Boise State"

    def import_datafile(self, fn, rec):
        # Read in XML
        et = XML(open(fn, 'rb').read())
        et = strip_ns_prefix(et)
        return self.__import_element_tree(et)

    def __import_element_tree(self, et):
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
            session._sample = self.sample(igsn=igsn, name=name)

        fractions = et.find("analysisFractions")

        for i,f in enumerate(fractions):
            s = self.import_analysis(f, session_index=i, analysis_type="analysisFraction")
            s._session = session
            self.db.session.add(s)

        s1 = self.import_dates(et.find("sampleDateModels"))
        s1._session = session
        self.db.session.add(s1)
        self.db.session.add(session)
        return session

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

        try:
            return self.datum(parameter, value,
                error=text(et, 'oneSigma'),
                error_metric=text(et, 'uncertaintyType'))
        except DataError as err:
            raise SparrowImportError(str(err.orig).strip())
