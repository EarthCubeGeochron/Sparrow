from sys import exit
from os import environ, listdir, path
from click import command, option, echo, secho, style
from  .extract_tables import extract_data_tables

def extract_analysis(fn):
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
    for fn in listdir(directory):
        dn = path.join(directory, fn)
        if not path.isdir(dn): continue

        echo("Irradiation "+style(fn, bold=True))
        for fn in listdir(dn):
            if path.splitext(fn)[1] != '.xls': continue
            echo(fn)
            fp = path.join(dn, fn)
            try:
                extract_analysis(fp)
            except Exception as err:
                if stop_on_error: raise err
                secho(str(err), fg='red')
                echo("")
