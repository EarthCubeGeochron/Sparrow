import gzip
from io import StringIO
from os import stat
from pandas import read_excel
from xlrd import open_workbook, XLRDError
from click import command, echo, secho, style
from sparrow.import_helpers import SparrowImportError, md5hash
from sparrow import Database
from sqlalchemy.dialects.postgresql import insert, BYTEA
from datetime import datetime

def extract_datatable(infile):
    try:
        wb = open_workbook(infile, on_demand=True)
        df = read_excel(wb, sheet_name="datatable", header=None)
    except XLRDError:
        if "AGE PICK" in infile.stem:
            raise NotImplementedError("AGE PICK files are not yet handled")
        raise SparrowImportError("No data table")

    b = StringIO()
    df.to_csv(b, compression='gzip')
    b.seek(0)
    # Convert to a binary representation
    return b.read().encode()

def import_datafile(db, infile):
    """
    Import the `datafile` Excel sheet to a CSV representation
    stored within the database that can be further processed without
    large filesystem operations. This also stores the original file's
    hash in order to skip importing unchanged data.

    Returns boolean (whether file was imported).
    """
    res = stat(infile)
    mtime = datetime.utcfromtimestamp(res.st_mtime)

    hash = md5hash(infile)

    data_file = db.model.data_file

    # Should maybe make sure error is not set
    rec = db.get(data_file, hash)
    # We are done if we've already imported
    if rec is not None:
        return False

    # Values to insert
    cols = dict(
        file_hash=hash,
        file_mtime=mtime,
        basename=infile.stem,
        csv_data=None)

    try:
        cols['csv_data'] = extract_datatable(infile)
    except NotImplementedError as e:
        secho(str(e), fg='red', dim=True)

    tbl = data_file.__table__
    sql = (insert(tbl)
        .values(file_path=str(infile), **cols)
        .on_conflict_do_update(
            index_elements=[tbl.c.file_path],
            set_=dict(**cols)))
    db.session.execute(sql)
    return True
