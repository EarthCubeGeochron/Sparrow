#!/usr/bin/env python

from os import environ
from click import command, option, echo, secho, style
from pathlib import Path
from sparrow import Database
from sparrow.import_helpers import SparrowImportError
from itertools import chain

from .extract_datatable import import_datafile

@command()
@option('--stop-on-error', is_flag=True, default=False)
@option('--verbose','-v', is_flag=True, default=False)
def cli(stop_on_error=False, verbose=False):
    """
    Import LaserChron files
    """
    varname = "LASERCHRON_DATA_DIR"
    env = environ.get(varname, None)
    if env is None:
        v = style(varname, fg='cyan', bold=True)
        echo(f"Environment variable {v} is not set.")
        secho("Aborting", fg='red', bold=True)
        return
    path = Path(env)
    assert path.is_dir()

    db = Database()

    files = chain(path.glob("**/*.xls"), path.glob("**/*.xls[xm]"))
    for f in files:
        try:
            secho(str(f), dim=True)
            import_datafile(db, f)
            db.session.commit()
        except (SparrowImportError, NotImplementedError) as e:
            if stop_on_error: raise e

            db.session.rollback()
            secho(str(e), fg='red')
