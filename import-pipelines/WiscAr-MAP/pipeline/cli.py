from sys import exit
from os import environ, listdir, path
from click import command, option, echo, secho, style
from pandas import read_excel, Series, concat
import numpy as N

def value_index(df, value, integer=False):
    for i, row in df.iterrows():
        for j, col in row.iteritems():
            if col != value: continue
            if integer:
                i = df.index.get_loc(i)
                j = df.columns.get_loc(j)
            return (i,j)

def extract_results_table(df):
    ixc = value_index(df, "Results")
    col = df.columns.get_loc(ixc[1])
    results = (df.iloc[ixc[0]:,col:]
            .dropna(axis=0, how='all')
            .dropna(axis=1, how='all'))
    results = results.rename(columns=results.iloc[0]).iloc[2:]

    ## Extract total fusion data

    try:
        plateau_comment = results.iloc[0,0].split('\n')[1]
    except IndexError:
        plateau_comment = None
    print(plateau_comment)
    results.iloc[0,0] = 'Age Plateau'

    ar = '39Ar(k)'

    results.set_index(results.iloc[:,0], inplace=True)
    results = results.iloc[:,1:]
    ## Ignore most of the table (past the ages) for now
    #ix = results.columns.get_loc('MSWD')
    ix = results.index.get_loc('Total Fusion Age')
    age_plateau = results.iloc[:ix,:]
    total_fusion = results.iloc[ix:,:]

    ix = ('Total Fusion Age', ar)
    val = total_fusion.loc[ix]
    total_fusion.loc[ix] = N.nan
    total_fusion.loc['Total Fusion Age', 'n_steps'] = val

    table_parts = [total_fusion]

    plateau_confidence = None
    if plateau_comment != 'Cannot Calculate':
        # Get n_steps out from 39Ar percentage
        val = age_plateau.loc[N.nan, ar]
        age_plateau.loc[N.nan, ar] = N.nan
        age_plateau.loc['Age Plateau', 'n_steps'] = val

        # Extract confidence on plateau fit
        # Find the first matching measure of confidence
        for v in ["2σ Confidence Limit","1σ Confidence Limit","Statistical T Ratio"]:
            ix = value_index(age_plateau, v, integer=True)
            if ix is not None: break
        loc = N.index_exp[ix[0]:ix[0]+2,ix[1]-1:ix[1]+1]
        conf = age_plateau.iloc[loc].copy()
        age_plateau.iloc[loc] = N.nan

        conf = (conf.set_index(conf.columns[1])
                    .transpose())
        conf.columns.name = None
        conf.index = ['Age Plateau']
        plateau_confidence = conf

        table_parts.insert(0, age_plateau)

    for a in table_parts:
        errors = a.iloc[2:].copy().transpose().dropna(how='all')
        a.insert(4, errors.columns[0], errors.iloc[0,0])
        a.insert(5, errors.columns[1], errors.iloc[0,1])
        # We drop remaining rows including those with % errors,
        # since the errors in age units are more interesting anyway
        a.drop(a.tail(3).index, axis=0, inplace=True)

    results = concat(table_parts)

    if plateau_confidence is not None:
        # Merge age plateau confidence info back in to combined data frame
        results = results.merge(plateau_confidence, how='left',
                                left_index=True, right_index=True)
    return results

def extract_data_tables(fn):
    # Create a `Pandas` representation of the entire first sheet of the spreadsheet
    df = read_excel(fn, sheet_name="Incremental Heating Summary")

    # Get the upper-left index of several subtables
    ixa = value_index(df, "Incremental\nHeating")
    ixb = value_index(df, "Information\non Analysis")

    # Clean the Incremental Heating table
    incremental_heating = (df.iloc[ixa[0]:ixb[0],:]
        .dropna(axis=0, how='all')
        .dropna(axis=1, how='all'))
    #incremental_heating.drop(len(incremental_heating)-1, inplace=True)
    incremental_heating.drop(1, inplace=True)
    incremental_heating.drop(incremental_heating.tail(1).index, inplace=True)

    # Clean Information on Analysis
    col = df.columns.get_loc(ixb[1])
    info = df.iloc[ixb[0]+1:,col:col+1].dropna()
    # Expand key/value pairs
    info = info.iloc[:,0].str.split("=", n=1, expand=True)
    info.set_index(0, inplace=True)
    info.index.names = ['key']
    info.columns.names = ['value']

    results = extract_results_table(df)

    #print(incremental_heating, info, results)
    return incremental_heating, info, results

def extract_analysis(fn):
    # Extract data tables from Excel sheet
    incremental_heating, info, results = extract_data_tables(fn)

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
