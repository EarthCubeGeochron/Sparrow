from click import echo, secho

from ..database import Database
from ..util import working_directory
from .util import md5hash, SparrowImportError
from .importer import BaseImporter

def iterfiles(import_function, file_sequence):
    db = Database()
    for f in file_sequence:
        try:
            secho(str(f), dim=True)
            imported = import_function(db, f)
            db.session.commit()
            if not imported:
                secho("Already imported", fg='green', dim=True)
        except (SparrowImportError, NotImplementedError) as e:
            if stop_on_error: raise e
            db.session.rollback()
            secho(str(e), fg='red')
