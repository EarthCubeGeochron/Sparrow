import gzip
from io import StringIO
from pandas import read_excel
from xlrd import XLRDError
from sparrow.import_helpers import SparrowImportError

def extract_datatable(infile):
    try:
        df = read_excel(infile, sheet_name="datatable", header=None)
    except XLRDError:
        raise SparrowImportError("No data table")

    b = StringIO()
    df.to_csv(b, compression='gzip')
    b.seek(0)
    return b
