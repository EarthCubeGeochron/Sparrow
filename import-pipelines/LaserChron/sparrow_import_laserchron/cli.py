#!/usr/bin/env python

from os import environ
from click import command, echo, secho, style
from pathlib import Path
from sparrow.import_helpers import SparrowImportError
from itertools import chain

from .extract_datatable import import_datafile

@command()
def cli(test=True):
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

    files = chain(path.glob("**/*.xls"), path.glob("**/*.xls[xm]"))
    for f in files:
        try:
            secho(str(f), dim=True)
            import_datafile(f)
        except (SparrowImportError, NotImplementedError) as e:
            secho(str(e), fg='red')
