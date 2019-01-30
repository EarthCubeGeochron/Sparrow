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

    def get(c, **kwargs):
        return get_or_create(db.session, c, **kwargs)

    project = get(cls.project,id=info.pop('Project'))
    project.title = project.id
    sample = get(cls.sample,
        id=info.pop('Sample'))
    sample.project = project.id
    db.session.add(sample)
    target = get(cls.material, id=info.pop('Material'))

    instrument = get(cls.instrument,
        name="MAP 215-50")

    method = get(cls.method,
        id="Ar/Ar "+info.pop("Type"))

    session = get(cls.session,
        sample_id=sample.id,
        instrument=instrument.id,
        technique=method.id,
        target=target.id)
    session.data = info.to_dict()
    db.session.add(session)

    get(cls.error_metric,
        id='1s', description='1 standard deviation',
        authority='WiscAr')

    parameter = get(
        cls.parameter,
        id="Tstep",
        description="Temperature of heating step",
        authority="WiscAr")

    unit = get(cls.unit, id="°C")

    dtype_temp = get(cls.datum_type,
        parameter=parameter.id,
        unit=unit.id,
        is_computed=False,
        is_interpreted=False)
    dtype.description = 'Temperature of heating step'
    db.session.add(dtype)

    i = 0
    for ix, row in incremental_heating.iterrows():
        analysis = get(cls.analysis,
            session_id=session.id,
            session_index=i,
            step_id=ix
        )
        analysis.in_plateau=row['in_plateau']
        analysis.is_interpreted = False
        db.session.add(analysis)
        i += 1



        import IPython; IPython.embed(); raise
    #
    # df = ['temperature',
    #      'in_plateau',
    #      '36Ar(a)',
    #      '37Ar(ca)',
    #      '38Ar(cl)',
    #      '39Ar(k)',
    #      '40Ar(r)',
    #      'Age',
    #      '± 2s',
    #      '40Ar(r)',
    #      '39Ar(k)',
    #      'K/Ca',
    #      '± 2s']

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
