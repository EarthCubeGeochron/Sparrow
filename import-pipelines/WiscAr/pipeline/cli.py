from sys import exit
from os import environ, listdir, path
from datetime import datetime
from click import command, option, echo, secho, style
from pathlib import Path
from sparrow import Database
from sparrow.database import get_or_create
from sparrow.import_helpers import BaseImporter

from .extract_tables import extract_data_tables
from .insert_data import extract_analysis

class ArArCalcImporter(BaseImporter):
    authority = "WiscAr"
    def __init__(self, db, **kwargs):
        super().__init__(db)
        self.verbose = kwargs.pop("verbose", False)

    def import_datafile(self, fn, rec, **kwargs):
        return extract_analysis(self.db, fn, verbose=self.verbose)

@command(name="import-map")
@option('--stop-on-error', is_flag=True, default=False)
@option('--verbose','-v', is_flag=True, default=False)
def cli(stop_on_error=False, verbose=False):
    """
    Import WiscAr MAP spectrometer data (ArArCalc files) in bulk.
    """
    _ = environ.get("SPARROW_DATA_DIR")
    directory = Path(_)/"MAP-Irradiations"

    db = Database()
    importer = ArArCalcImporter(db, verbose=verbose)

    importer.iterfiles(
        directory.glob("**/*.xls"),
        stop_on_error=stop_on_error)
