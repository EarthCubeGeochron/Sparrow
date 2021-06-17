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
    if v == "":
        return None
    return v


def strip_ns_prefix(tree):
    # xpath query for selecting all element nodes in namespace
    query = "descendant-or-self::*[namespace-uri()!='']"
    # for each element returned by the above xpath query...
    for element in tree.xpath(query):
        # replace element name with its local name
        element.tag = QName(element).localname
    return tree


class ETReduxImporter(BaseImporter):
    """
    A Sparrow importer for Geochron.org ETRedux XML
    """

    authority = "Boise State"

    def import_datafile(self, fn, rec):
        # Read in XML
        et = XML(open(fn, "rb").read())
        et = strip_ns_prefix(et)
        return self.__import_element_tree(et)

    def __import_element_tree(self, et):
        """
        Aliquot -> session
        """
        dates = [i.text for i in et.findall(".//dateCertified")]
        date = max(set(dates), key=dates.count)
        if not date:
            date = datetime.min()

        # Set IGSN
        igsn = text(et, "aliquotIGSN")
        if str(igsn) == "0":
            igsn = None

        sample = None
        # Import analysis sessions
        sample_igsn = text(et, "sampleIGSN")
        if str(igsn) == "0":
            igsn = None
        name = text(et, "aliquotName")
        if igsn or name:
            sample = self.sample(igsn=sample_igsn, name=name)

        session = self.db.get_or_create(
            self.m.session, date=date, igsn=igsn, sample_id=sample.id
        )
        self.db.session.flush()

        # Set publication
        ref = text(et, "aliquotReference")
        if ref:
            session._publication = self.publication(ref)

        fractions = et.find("analysisFractions")

        for i, f in enumerate(fractions):
            s = self.import_analysis(
                f, session, session_index=i, analysis_type="analysisFraction"
            )

        s1 = self.import_dates(et.find("sampleDateModels"), session)

        self.db.session.add(session)
        return session

    def import_dates(self, et, session):
        """
        SampleDateModel -> analysis(interpreted: true)
        """
        models = et.findall("SampleDateModel")

        analysis = self.add_analysis(
            session,
            is_interpreted=True,
            is_standard=False,
            analysis_type="Interpreted Age",
        )
        self.db.session.flush()

        for d in models:
            self.import_datum(analysis, d)

        return analysis

    def import_analysis(self, et, session, **kwargs):
        """
        AnalysisFraction -> analysis
        """

        def data_iterator(et, key, unit, model="ValueModel"):
            return iter(et.find(key).findall(model))

        data = chain(
            data_iterator(et, "analysisMeasures", "unknown"),
            data_iterator(
                et, "measuredRatios", "ratio_measured", model="MeasuredRatioModel"
            ),
            data_iterator(et, "radiogenicIsotopeRatios", "ratio_radiogenic"),
        )

        analysis = self.add_analysis(session, **kwargs)

        for d in data:
            res = self.import_datum(analysis, d)

        return analysis

    def import_datum(self, analysis, et):
        """
        ValueModel -> datum
        """
        parameter = et.find("name").text
        try:
            value = et.find("value").text
            assert float(value) is not None
        except:
            return None

        try:
            return self.datum(
                analysis,
                parameter,
                value,
                error=text(et, "oneSigma"),
                error_metric=text(et, "uncertaintyType"),
            )
        except DataError as err:
            raise SparrowImportError(str(err.orig).strip())
