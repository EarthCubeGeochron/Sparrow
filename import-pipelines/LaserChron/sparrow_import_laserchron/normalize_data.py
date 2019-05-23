from math import isnan
from click import secho
from pandas import concat, to_numeric
import re

from sparrow.import_helpers import SparrowImportError

def merge_cols(d):
    v1 = d.iloc[0]
    v2 = d.iloc[1]

    try:
        if isnan(v2): return v1
    except:
        pass

    v = (v1,v2)
    if "Pb" in v1 or "Th" in v2:
        return "/".join(v)
    return " ".join(v)

def table_metadata(headers):
    columns = headers.apply(merge_cols, axis=0)
    units = columns.str.extract('\((.+)\)').iloc[:,0]

    # Extract units and make sure all are defined
    for i, u in enumerate(units):
        if str(u) != 'nan': continue
        next_col_unit = units.iat[i+1]
        c = columns.iat[i]
        this_unit = None
        if next_col_unit == 'Ma':
            # Set this unit to Ma...
            units.iat[i] = 'Ma'
            columns.iat[i] = str(c)+" age"
        elif next == '%':
            units.iat[i] = 'ratio'
        elif "/" in c and not "age" in c:
            units.iat[i] = 'ratio'
        elif 'error corr' in c:
            units.iat[i] = 'dimensionless'

    # Get rid of units
    columns = columns.str.strip().str.replace(' \(.+\)$',"")

    for i,col in enumerate(columns):
        if col.strip() != '±': continue
        columns.iat[i] = columns.iat[i-1]+" error"

    # Make sure that we have defined units for all columns
    try:
        assert not units.isnull().values.any()
        assert not columns.isnull().values.any()
    except AssertionError:
        print(columns, units)

    # Clean columns
    # ...this is kinda ridiculous
    ix = (columns
        .str.replace("[\*\/\s\.]+"," ")
        .str.strip()
        .str.replace("^(\d{3}\w{1,2}\s\d{3}\w{1,2}) age", r"age \1")
        .str.replace("Best age", "best age")
        .str.replace("^Conc$","concordance")
        .str.replace("\s+","_"))

    meta = (concat((columns, units), axis=1)
            .transpose()
            .rename(columns=ix))
    meta.columns.name = "Column"
    meta.index = ["Description", "Unit"]
    meta.loc["Description", "U"] = "Uranium concentration"
    meta.loc["Description", "concordance"] = "Concordance"

    return meta

def normalize_data(df):
    if df.iloc[0,0].startswith("Table"):
        df = df[1:]

    # Drop empty rows
    df = df.dropna(how='all')

    # Drop columns that are empty in the header
    # Note: this does not preserve comments and some other metadata;
    # we may want to.
    header = df.iloc[1:3, 1:]
    # Make sure second row of header (chiefly units) is set to null
    # if first row is null (this helps get rid of trailing end matter)
    header.iloc[1] = header.iloc[1].mask(header.iloc[0].isnull())
    header = header.dropna(axis=1, how='all')
    meta = table_metadata(header)

    body = df.iloc[3:].set_index(df.columns[0])
    body.index.name = 'Analysis'
    # Make sure data is the same shape as headers
    data = (body.drop(body.columns.difference(header.columns), 1)
                .dropna(how='all'))

    # We've found a few empty data frames
    if data.empty:
        raise SparrowImportError('Empty dataframe')

    try:
        assert data.shape[1] == meta.shape[1]
    except AssertionError:
        raise SparrowImportError('Data frame is not correct shape')

    # For some reason we have a lot of these closed brackets in data files
    data.index = data.index.str.replace(' <>','').str.strip()
    data.columns = meta.columns

    ncols = 19
    if data.shape[1] == ncols:
        return data, meta

    if len(data.columns[:ncols].intersection(data.columns[ncols:])) > 0:
        secho("Ignoring duplicate output columns.")
        data = data.iloc[:,:ncols]
        meta = meta.iloc[:,:ncols]

    return data, meta

def extract_session_index(sample_name):
    pat = r"[\.\:_\s-](\w+)$"
    try:
        s = re.search(pat, str(sample_name))
    except TypeError:
        return None
    if s is not None:
        return s.group(1)

    pat = r"(\d+)$"
    s = re.search(pat, str(sample_name))
    if s is not None:
        return s.group(1)
    return None

def remove_suffix(s1, s2):
    if s1.endswith(s2):
        return s1[:-len(s2)]
    return s1

def strip_session_index(row):
    s1 = str(row.at['sample_id'])
    s2 = str(row.at['session_ix'])
    v = (remove_suffix(s1,s2)
        .rstrip('.:_- '))
    row.at['sample_id'] = v
    return row

def generalize_samples(data):
    # Create sample name columns
    data.reset_index(inplace=True)
    samples = data['analysis'].str.strip()
    session_ix = samples.apply(extract_session_index)

    # Session index should be integer, so we set things that don't match
    # to NaNs
    data['session_ix'] = to_numeric(session_ix, errors='coerce')
    data['sample_id'] = samples
    d1 = data.apply(strip_session_index, axis=1)

    return d1.set_index(["sample_id", "session_ix"], drop=True)
