from sparrow import Database
from pandas import read_csv
from io import StringIO
from click import echo, secho
from .read_data import extract_data
from sparrow.import_helpers import SparrowImportError

def normalize_table(db, rec):
    tbl = rec.csv_data
    if tbl is None:
        return
    f = StringIO()
    f.write(tbl.decode())
    f.seek(0)
    df = read_csv(f)
    df = df.iloc[:,1:]
    df = extract_data(df)

def import_datafile(db, rec):
    if "NUPM-MON" in rec.basename:
        raise SparrowImportError("NUPM-MON files are not handled yet")
    data = normalize_table(db, rec)

def normalize_data():
    db = Database()
    query = db.session.query(db.model.data_file)

    for rec in query:
        secho(rec.file_path, fg="cyan")
        try:
            import_datafile(db, rec)
        except SparrowImportError as err:
            secho(str(err), fg='red')
