from sys import exit
from os import environ, listdir, path
from datetime import datetime
from click import command, option, echo, secho, style
from sparrow import Database
from sparrow.import_helpers import SparrowImportError
from sparrow.database import get_or_create

from  .extract_tables import extract_data_tables

def print_dataframe(df):
    secho(str(df.fillna(''))+'\n', dim=True)

def add_datum(db, analysis, **kwargs):
    cls = db.model
    dtype_cols = [i for i in
        cls.datum_type.__table__.columns.keys()
        if i != 'id']
    defaults = dict(
        is_computed=False,
        is_interpreted=False)
    dtype_kw = dict()
    for i in dtype_cols:
        val = kwargs.pop(i, defaults.get(i, None))
        if val is not None:
            dtype_kw[i] = val
    dtype = db.get_or_create(cls.datum_type, **dtype_kw)
    kwargs['type'] = dtype.id
    kwargs['analysis'] = analysis.id
    return db.get_or_create(cls.datum, **kwargs)

def add_K_Ca_ratio(db, analysis, row):
    ratio = db.get_or_create('unit',
        id='ratio', authority="WiscAr")

    ix = list(row.index).index('K/Ca')
    error_ix = ix+1
    em = get_error_metric(db, row.index[error_ix])
    add_datum(db, analysis,
        value=row['K/Ca'],
        unit=ratio.id,
        parameter=db.get_or_create("parameter", id="K/Ca").id,
        description="Potassium/Calcuim ratio",
        error=row.iloc[error_ix],
        error_metric=em.id,
        error_unit=ratio.id)

def get_error_metric(db, label):
    error_metric = label.replace("± ","")
    description = ""
    if error_metric == '1s':
        description = "1 standard deviation"
    elif error_metric == '2s':
        description = "2 standard deviations"
    return db.get_or_create('error_metric',
        id=error_metric, description=description)

def import_shared_parameters(db, analysis, row):
    add_K_Ca_ratio(db, analysis, row)

    ratio = db.get_or_create('unit',
        id='ratio', authority="WiscAr")

    id = 'plateau_age'
    if analysis.analysis_type == 'Total Fusion Age':
        id = 'total_fusion_age'

    age_parameter = db.get_or_create("parameter", id=id)
    Ma = db.get_or_create("unit", id='Ma')

    ix = list(row.index).index('Age')
    error_ix = ix+1
    em = get_error_metric(db, row.index[error_ix])

    add_datum(db, analysis,
        value=row['Age'],
        unit=Ma.id,
        parameter=age_parameter.id,
        error=row.iloc[error_ix],
        error_metric=em.id,
        is_computed=True,
        error_unit=Ma.id)

    ## 40Ar/39Ar(k) ratio
    label = '40(r)/39(k)'
    parameter = db.get_or_create("parameter", id=label)
    ix = list(row.index).index(label)
    error_ix = ix+1
    el = row.index[error_ix]
    em = get_error_metric(db, el)
    add_datum(db, analysis,
        value=row[label],
        unit=ratio.id,
        parameter=parameter.id,
        error=row.iloc[error_ix],
        error_metric=em.id,
        is_interpreted=True,
        is_computed=True,
        error_unit=ratio.id)

    row.drop(index=['Age','K/Ca',label, el], inplace=True)
    return row

def import_age_plateau(db, analysis_session, row):

    analysis = db.get_or_create('analysis',
        session_id = analysis_session.id,
        is_interpreted=True,
        analysis_type='Age Plateau')

    row = import_shared_parameters(db, analysis, row)

    parameter = db.get_or_create('parameter',
        id='39Ar(k) plateau [%]',
        description="39Ar from potassium, cumulative percent released in all plateau steps",
        authority='WiscAr')

    add_datum(db, analysis,
        value=row.pop('39Ar(k)'),
        unit='%',
        parameter=parameter.id,
        is_interpreted=True,
        is_computed=True)

    analysis.data = row.dropna().to_dict()
    db.session.add(analysis)

def import_fusion_age(db, analysis_session, row):

    analysis = db.get_or_create('analysis',
        session_id = analysis_session.id,
        is_interpreted=True,
        analysis_type='Total Fusion Age')
    row = import_shared_parameters(db, analysis, row)
    analysis.data = row.dropna().to_dict()
    db.session.add(analysis)

def extract_analysis(db, fn, verbose=False):
    # Extract data tables from Excel sheet

    # File modification time is right now the best proxy
    # for creation date (note: sessions will be duplicated
    # if input files are changed)
    mod_time = datetime.fromtimestamp(path.getmtime(fn))
    cls = db.mapped_classes
    existing_session = db.session.query(cls.session).filter_by()

    try:
        incremental_heating, info, results = extract_data_tables(fn)
    except Exception as exc:
        raise SparrowImportError(str(exc))
    if verbose:
        print_dataframe(incremental_heating)
        print_dataframe(info)
        print_dataframe(results.transpose())

    def get(c, **kwargs):
        return get_or_create(db.session, c, **kwargs)

    project = get(cls.irradiation,id=info.pop('Project'))
    project.title = project.id

    sample = get(cls.sample,
        name=info.pop('Sample'))
    db.session.add(sample)
    target = get(cls.material, id=info.pop('Material'))

    instrument = get(cls.instrument,
        name="MAP 215-50")

    method = get(cls.method,
        id="Ar/Ar "+info.pop("Type"))

    session = get(cls.session,
        sample_id=sample.id,
        date=mod_time,
        instrument=instrument.id,
        technique=method.id,
        target=target.id)
    session.irradiation_id = project.id
    session.data = info.to_dict()
    db.session.add(session)

    get(cls.error_metric,
        id='1s', description='1 standard deviation',
        authority='WiscAr')

    param_data = {
        'Tstep': "Temperature of heating step",
        'power': "Laser power of heating step",
        '36Ar(a)': "36Ar, corrected for air interference",
        '37Ar(ca)': "37Ar, corrected for Ca interference",
        '38Ar(cl)': "38Ar, corrected for Cl interference",
        '39Ar(k)': "39Ar, corrected for amount produced by K",
        '40Ar(r)': "Radiogenic 40Ar measured abundance",
        '40(r)/39(k)': "Ratio of radiogenic 40Ar to 39Ar from K",
        'step_age': "Age calculated for a single heating step",
        'plateau_age': "Age calculated for a plateau",
        'total_fusion_age': "Age calculated for fusion of all heating steps",
        '40Ar(r) [%]': "Radiogenic 40Ar, percent released in this step",
        '39Ar(k) [%]': "39Ar from potassium, percent released in this step",
        'K/Ca': "Potassium/Calcium ratio"
    }

    V = get(cls.unit, id='V',
            description='Measured isotope abundance',
            authority='WiscAr')
    percent = get(cls.unit, id='%')
    degrees_c = get(cls.unit, id="°C")
    Ma = get(cls.unit, id='Ma')
    ratio = get(cls.unit, id='ratio', authority="WiscAr")

    p = {}
    for k,v in param_data.items():
        p[k] = get(
            cls.parameter,
            id=k,
            authority="WiscAr")
        p[k].description = v
        db.session.add(p[k])

    i = 0
    for ix, row in incremental_heating.iterrows():
        analysis = get(cls.analysis,
            session_id=session.id,
            session_index=i,
            analysis_type=ix
        )
        analysis.in_plateau = row['in_plateau']
        analysis.is_interpreted = False
        db.session.add(analysis)
        i += 1

        def datum(**kwargs):
            return add_datum(db, analysis, **kwargs)

        # Check whether we are measuring laser power or temperature
        s = incremental_heating['temperature']
        if (s<=100).sum() == len(s):
            # Everything is less than 100
            datum(
                parameter=p['power'].id,
                unit=percent.id,
                description='Laser power for heating step',
                value=row['temperature'])
        else:
            datum(
                parameter=p['Tstep'].id,
                unit=degrees_c.id,
                description='Temperature of heating step',
                value=row['temperature'])

        for r in ['36Ar(a)','37Ar(ca)','38Ar(cl)','39Ar(k)',
                  '40Ar(r)','39Ar(k) [%]','40Ar(r) [%]']:
            unit = V
            if '[%]' in r:
                unit = percent
            datum(
                parameter=p[r].id, unit=unit.id,
                description=p[r].description,
                value=row[r])

        ix = list(row.index).index('Age')
        error_ix = ix+1
        em = get_error_metric(db, row.index[error_ix])

        datum(value=row['Age'],
            unit=Ma.id,
            parameter=p['step_age'].id,
            description="Age of heating step",
            error=row.iloc[error_ix],
            error_metric=em.id,
            error_unit=Ma.id)

        add_K_Ca_ratio(db, analysis, row)

    # Import results table
    try:
        res = results.loc["Age Plateau"]
        import_age_plateau(db, session, res)
    except KeyError:
        pass

    res = results.loc["Total Fusion Age"]
    import_fusion_age(db, session, res)

    # This function returns the top-level
    # record that should be linked to the datafile
    return session
