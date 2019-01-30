from sys import exit
from os import environ, listdir, path
from click import command, option, echo, secho, style
from labdata import Database
from labdata.database import get_or_create

from  .extract_tables import extract_data_tables

def print_dataframe(df):
    secho(str(df.fillna(''))+'\n', dim=True)

def extract_analysis(db, fn, verbose=False):
    # Extract data tables from Excel sheet
    incremental_heating, info, results = extract_data_tables(fn)
    if verbose:
        print_dataframe(incremental_heating)
        print_dataframe(info)
    print_dataframe(results.transpose())

    cls = db.mapped_classes

    get_or_create(db.session, cls.error_metric,
        id='1s', description='1 standard deviation',
        authority='WiscAr')
    db.session.commit()

    import IPython; IPython.embed(); raise

@command(name="import-map")
@option('--stop-on-error', is_flag=True, default=False)
@option('--verbose','-v', is_flag=True, default=False)
def cli(stop_on_error=False, verbose=False):
    """
    Import WiscAr MAP spectrometer data (ArArCalc files) in bulk.
    """
    directory = environ.get("WISCAR_MAP_DATA")
    db = Database()

    for fn in listdir(directory):
        dn = path.join(directory, fn)
        if not path.isdir(dn): continue

        echo("Irradiation "+style(fn, bold=True))
        for fn in listdir(dn):
            if path.splitext(fn)[1] != '.xls': continue
            echo(fn)
            fp = path.join(dn, fn)
            try:
                extract_analysis(db, fp, verbose=verbose)
            except Exception as err:
                if stop_on_error: raise err
                secho(str(err), fg='red')
                echo("")
