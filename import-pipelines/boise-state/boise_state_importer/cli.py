from os import environ
from click import command, option, echo, secho, style
from pathlib import Path
from sparrow import Database
from sparrow.import_helpers import SparrowImportError, working_directory
from .import_datafile import import_datafile

def iterfiles(import_function, file_sequence):
    db = Database()
    for f in file_sequence:
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
def cli(stop_on_error=False, verbose=False):
    """
    Import Boise State XML files
    """
    varname = "SPARROW_DATA_DIR"
    env = environ.get(varname, None)
    if env is None:
        v = style(varname, fg='cyan', bold=True)
        echo(f"Environment variable {v} is not set.")
        secho("Aborting", fg='red', bold=True)
        return
    path = Path(env)
    assert path.is_dir()

    files = path.glob("**/*.xml")
    iterfiles(import_datafile, files)
