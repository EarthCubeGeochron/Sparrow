#!/usr/bin/env python

from os import environ
from click import command, option, argument, echo, secho, style
from pathlib import Path
from sparrow import Database
from sparrow.import_helpers import SparrowImportError, working_directory
from itertools import chain

from .extract_datatable import import_datafile
from .laserchron_importer import LaserchronImporter

def extract_data(db, stop_on_error=False):
    path = Path('.')
    files = chain(path.glob("**/*.xls"), path.glob("**/*.xls[xm]"))
    for f in files:
        try:
            secho(str(f), dim=True)
            imported = import_datafile(db, f)
            db.session.commit()
            if not imported:
                secho("Already imported", fg='green', dim=True)
        except (SparrowImportError, NotImplementedError) as e:
            if stop_on_error: raise e
            db.session.rollback()
            secho(str(e), fg='red')

@command()
@option('--stop-on-error', is_flag=True, default=False)
@option('--verbose','-v', is_flag=True, default=False)
@option('--extract/--no-extract', default=False)
@option('--normalize/--no-normalize', default=True)
@option('--redo', default=False, is_flag=True)
@argument('basename', required=False, nargs=-1)
def cli(basename=None, stop_on_error=False, verbose=False, extract=False, normalize=True, redo=False):
    """
    Import LaserChron files
    """
    varname = "SPARROW_DATA_DIR"
    for var in ["SPARROW_S3_ENDPOINT", "SPARROW_S3_BUCKET", "SPARROW_S3_KEY", "SPARROW_S3_SECRET"]:
        env = environ.get(varname, None)
        if env is None:
            v = style(varname, fg='cyan', bold=True)
            echo(f"Environment variable {v} is not set.")
            secho("Aborting", fg='red', bold=True)
            return

    db = Database()
    if extract:
        extract_data(db)
    importer = LaserchronImporter(db)
    if normalize and not basename:
        importer.import_all(redo=redo)
        return
    basename = 'CONOR 010205, 123001, CDO-308-6 NUPMagecalc'
    if basename:
        importer.import_one(basename)
