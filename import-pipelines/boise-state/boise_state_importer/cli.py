from os import environ
from click import Group, option, echo, secho, style
from pathlib import Path
from sparrow import Database

from .et_redux_importer import ETReduxImporter
from .import_metadata import import_metadata

cli = Group()


@cli.command(name="import-xml")
@option("--fix-errors", is_flag=True, default=False)
@option("--redo", is_flag=True, default=False)
def import_xml(**kwargs):
    """
    Import Boise State XML files
    """
    varname = "SPARROW_DATA_DIR"
    env = environ.get(varname, None)
    if env is None:
        v = style(varname, fg="cyan", bold=True)
        echo(f"Environment variable {v} is not set.")
        secho("Aborting", fg="red", bold=True)
        return
    path = Path(env)
    assert path.is_dir()

    db = Database()
    importer = ETReduxImporter(db)
    files = path.glob("**/*.xml")
    importer.iterfiles(files, **kwargs)


@cli.command(name="import-metadata")
@option("--download", is_flag=True, default=False)
def __import_metadata(download=False):
    """
    Import IGSN metadata from SESAR
    """
    import_metadata(download=download)
