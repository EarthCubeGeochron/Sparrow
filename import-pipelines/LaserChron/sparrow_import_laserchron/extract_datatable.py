import gzip
from io import StringIO
from pandas import read_excel
from xlrd import XLRDError
from click import command, echo, secho, style
from sparrow.import_helpers import SparrowImportError, md5hash
from sparrow import Database
from sqlalchemy.dialects.postgresql import insert, BYTEA

def extract_datatable(infile):
    try:
        df = read_excel(infile, sheet_name="datatable", header=None)
    except XLRDError:
        if "AGE PICK" in infile.stem:
            raise NotImplementedError("AGE PICK files are not yet handled")
        raise SparrowImportError("No data table")

    b = StringIO()
    df.to_csv(b, compression='gzip')
    b.seek(0)
    return b.read().encode()

def import_datafile(db, infile):

    hash = md5hash(infile)

    data_file = db.mapped_classes.data_file

    rec = db.get(data_file, hash)
    # We are done if we've already imported
    if rec is not None: return

    dt = extract_datatable(infile)

    # Run query to insert values
    cols = dict(
        hash=hash,
        basename=infile.stem,
        import_date=None,
        csv_data=dt)
    tbl = data_file.__table__
    sql = (insert(tbl)
        .values(file_path=str(infile), **cols)
        .on_conflict_do_update(
            index_elements=[tbl.c.file_path],
            set_=dict(**cols)))
    db.session.execute(sql)
