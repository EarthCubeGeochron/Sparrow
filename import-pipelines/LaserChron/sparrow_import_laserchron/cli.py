#!/usr/bin/env python

from os import environ
from click import command, echo, secho, style
from pathlib import Path

from sparrow_import_laserchron.extract_datatable import extract_datatable

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

    v = path.glob("**/*.xls[xm]")
    for fn in v:
        print(str(fn))
