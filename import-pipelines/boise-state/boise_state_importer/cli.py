from os import environ
from click import command, option, echo, secho, style
from pathlib import Path
from sparrow import Database
from sparrow.import_helpers import SparrowImportError, working_directory

def extract_data(path):
    db = Database()
    files = path.glob("**/*.xml")
    for f in files:
        secho(str(f), dim=True)

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
    extract_data(path)
