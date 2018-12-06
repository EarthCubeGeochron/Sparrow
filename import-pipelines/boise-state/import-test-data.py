import pandas as P
from xml.etree import ElementTree as ET
from sys import argv
from itertools import islice
from io import StringIO

def parse_xml(content):
    try:
        tree = ET.XML(content)
    except ET.ParseError as err:
        lineno, column = err.position
        line = next(islice(StringIO(content), lineno))
        caret = '{:=>{}}'.format('^', column)
        err.msg = '{}\n{}\n{}'.format(err, line, caret)
        raise
    return tree

with open(argv[1]) as f:
    et = parse_xml(f.read())
    import IPython; IPython.embed()
