from sys import exit
from os import environ, listdir, path
from click import command, option, echo, secho, style
from labdata import Database
from  .extract_tables import extract_data_tables

parameter = None
unit = None
datum_type = None
error_metric = None
def setup_tables(db):
    unit = db.reflect_table('unit', schema='vocabulary')
    parameter = db.reflect_table('parameter', schema='vocabulary')
    error_metric = db.reflect_table('error_metric', schema='vocabulary')
    datum_type = db.reflect_table('datum_type')

    # Insert correct error metrics

def insert_data_type(session):
    pass

def extract_analysis(session, fn):
    # Extract data tables from Excel sheet
    incremental_heating, info, results = extract_data_tables(fn)
    secho(str(results.transpose().fillna(''))+'\n', dim=True)

@command(name="import-map")
@option('--stop-on-error', is_flag=True, default=False)
def cli(stop_on_error=False):
    """
    Import WiscAr MAP spectrometer data (ArArCalc files) in bulk.
    """
    directory = environ.get("WISCAR_MAP_DATA")
    db = Database()
    setup_tables(db)

    for fn in listdir(directory):
        dn = path.join(directory, fn)
        if not path.isdir(dn): continue

        echo("Irradiation "+style(fn, bold=True))
        for fn in listdir(dn):
            if path.splitext(fn)[1] != '.xls': continue
            echo(fn)
            fp = path.join(dn, fn)
            try:
                extract_analysis(db.session, fp)
            except Exception as err:
                if stop_on_error: raise err
                secho(str(err), fg='red')
                echo("")
