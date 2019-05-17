"""
Import script for *ET-Redux* xml-formatted data
from Boise State Geochronology Laboratory
"""
from lxml.etree import tostring, XML, QName
from click import echo

from sparrow.import_helpers import md5hash
from .geochron_importer import GeochronImporter

def strip_ns_prefix(tree):
    #xpath query for selecting all element nodes in namespace
    query = "descendant-or-self::*[namespace-uri()!='']"
    #for each element returned by the above xpath query...
    for element in tree.xpath(query):
        #replace element name with its local name
        element.tag = QName(element).localname
    return tree

def import_datafile(db, filename):
    # Check whether file exists
    hash = md5hash(filename)
    data_file = db.mapped_classes.data_file
    rec = db.get(data_file, hash)
    if rec is not None:
        return False

    # Read in XML
    et = XML(open(filename, 'rb').read())
    et = strip_ns_prefix(et)
    #echo(tostring(et, pretty_print=True))

    importer = GeochronImporter(db)
    importer.import_datafile(et)

    return True
