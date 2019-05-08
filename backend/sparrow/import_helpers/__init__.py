from hashlib import md5
from click import echo, secho

from ..database import Database
from ..util import working_directory
from .importer import BaseImporter

class SparrowImportError(Exception):
    pass

def md5hash(fname):
    """
    Compute the md5 hash of a file (given by its name)
    """
    hash = md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

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
