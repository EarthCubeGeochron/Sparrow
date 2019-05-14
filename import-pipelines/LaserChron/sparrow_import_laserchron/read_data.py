from math import isnan
from click import secho

def itercells(df):
    for i, r in df.iterrows():
        for j, c in r.iteritems():
            yield (i,j), c

def find_last_column(df):
    last_col = None
    # Find last column of data based on
    # where "Concordia" column is
    for ix, c in itercells(df):
        try:
            assert c.lower().startswith("conc")
            last_col = ix
            break
        except (AssertionError, AttributeError):
            pass

    # Double check with another method (look
    # for columns that are _almost_ empty)
    # number of defined values in each column
    n_vals = df.isnull().values.sum(axis=0)
    n_rows = df.shape[0]
    last_col = next(i
        for (i,n) in list(enumerate(n_vals))[::-1]
        if n < n_rows/2)

    # These two methods serve as a sanity check
    # that we are dealing with a "normal" ETAgeCalc
    # or NuAgeCalc file
    ix = int(ix[1])
    assert ix >= last_col
    return ix

def extract_comments(df):
    # Knowing the last column of data, we serialize all later non-zero
    # values (assumed to be comments/annotations that might be worth carrying
    # along) into one comment field. These may not correspond directly to the
    # data row...
    comment_ix = last_col_ix+1
    data = df.iloc[:,:comment_ix+1]
    comments = df.iloc[:,comment_ix:]
    for i,row in comments.iterrows():
        v = list(row.dropna().values)
        if len(v) == 0: continue
        data.iloc[i,comment_ix] = ",".join(v)

def merge_cols(d):
    v1 = d.iloc[0]
    v2 = d.iloc[1]

    try:
        if isnan(v2): return v1
    except:
        pass

    v = (v1,v2)
    if "Pb" in v1:
        return "/".join(v)
    return " ".join(v)

def extract_data(df):
    if df.iloc[0,0].startswith("Table"):
        df = df[1:]

    df = df.dropna(how='all')
    head = df.iloc[:3]

    try:
        last_col_ix = find_last_column(df)
        df = df.iloc[:,:last_col_ix+1]
    except AssertionError:
        # We have a weird spreadsheet, but we will
        # print it but force it to conform for now

        #print(head.transpose())
        if len(df.columns) == 28:
            secho("Extra output block was dropped", fg='red')
        else:
            secho("Data frame too long", fg='red')
        df = df.iloc[:, :20]
    except StopIteration:
        # We have failed clearly
        return False

    # For now we don't do comments
    headers = df.iloc[1:3]
    h1 = headers.apply(merge_cols, axis=0)

    try:
        assert len(df.columns) == 20
    except AssertionError:
        print(df)

    head = df.iloc[:3]
    df1 = df.iloc[3:]

    return True
