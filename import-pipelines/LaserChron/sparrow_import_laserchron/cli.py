#!/usr/bin/env python

from os import environ
from click import command, echo, secho, style
from pathlib import Path
from sparrow.import_helpers import SparrowImportError

from .extract_datatable import extract_datatable

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

    v = path.glob("**/*.xls")
    for fn in v:
        print(str(fn))
        try:
            out = extract_datatable(fn)
        except SparrowImportError as e:
            secho(str(e), fg='red')

    v = path.glob("**/*.xls[xm]")
    for fn in v:
        print(str(fn))
