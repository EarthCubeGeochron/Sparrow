from hashlib import md5
from numpy import isnan
from os import environ
from pathlib import Path
from click import echo, style

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


def ensure_sequence(possible_iterator):
    try:
        return iter(possible_iterator)
    except TypeError:
        return [possible_iterator]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def coalesce_nan(value):
    if isnan(value):
        return None
    return value


def get_data_directory():
    varname = "SPARROW_DATA_DIR"
    env = environ.get(varname, None)
    if env is None:
        v = style(varname, fg='cyan', bold=True)
        echo(f"Environment variable {v} is not set.")
        secho("Aborting", fg='red', bold=True)
        return
    p = Path(env)
    assert p.is_dir()
    return p
