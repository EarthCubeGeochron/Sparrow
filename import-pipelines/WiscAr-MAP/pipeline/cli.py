from os import environ, listdir, path
from click import command, echo, secho, style
from pandas import read_excel

def extract_multiple_tables(df):
    """
    Extracts multiple tables separated by blank rows and columns
    """
    pass

def value_index(df, value):
    for i, row in df.iterrows():
        for j, col in row.iteritems():
            if col != value: continue
            return (i,j)

def extract_analysis(fn):
    df = read_excel(fn, sheet_name="Incremental Heating Summary")
    ixa = value_index(df, "Incremental\nHeating")
    ixb = value_index(df, "Information\non Analysis")
    ixc = value_index(df, "Results")

    # Clean the Incremental Heating table
    incremental_heating = (df.iloc[ixa[0]:ixb[0],:]
        .dropna(axis=0, how='all')
        .dropna(axis=1, how='all'))
    incremental_heating.drop(len(incremental_heating)-1, inplace=True)
    incremental_heating.drop(1, inplace=True)
    print(incremental_heating)
    # Clean Information on Analysis

@command(name="import-map")
def cli():
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
                secho(str(err), fg='red')
                echo("")
