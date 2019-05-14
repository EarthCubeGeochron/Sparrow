from sparrow import Database
from pandas import read_csv
from io import StringIO
from click import echo, secho
from .read_data import extract_data

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

def normalize_data():
    db = Database()
    query = db.session.query(db.model.data_file)

    for rec in query:
        secho(rec.file_path, fg="cyan")
        if "NUPM-MON" in rec.basename:
            secho("NUPM-MON files are not handled yet", fg='red')
            continue
        normalize_table(db, rec)
