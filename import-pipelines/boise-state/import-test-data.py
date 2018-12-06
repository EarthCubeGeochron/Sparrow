"""
Import script for *ET-Redux* xml-formatted data
from Boise State Geochronology Laboratory
"""

import pandas as P
import xml.etree.cElementTree as ET
from sys import argv
from itertools import islice
from io import StringIO

def parse_xml(content, strip_namespaces=True):
    if not strip_namespaces:
        return ET.XML(content)

    it = ET.iterparse(StringIO(content))
    for _, el in it:
        if '}' not in el.tag:
            continue
        el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
    return it.root

with open(argv[1]) as f:
    # Read in XML
    et = parse_xml(f.read())

for frac in et.iter('analysisFractions'):
    print(frac.attrib)
