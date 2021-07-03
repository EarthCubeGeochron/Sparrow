from hashlib import md5
from numpy import isnan
from os import environ
from pathlib import Path
from click import echo, secho, style
from io import IOBase


class SparrowImportError(Exception):
    pass


def get_file_object(name_or_obj, mode="rb"):
    """Get a reference to a data file if passed a file name, or pass through
    a file-like object unmodified.
    """
    if isinstance(name_or_obj, IOBase):
        return name_or_obj
    return open(name_or_obj, "rb")


def md5hash(fobj, rewind=True):
    """
    Compute the md5 hash of a file (given by its name)
    """
    if not isinstance(fobj, IOBase):
        # We were passed a string
        with open(fobj, "rb") as f:
            return md5hash(f)

    hash = md5()
    for chunk in iter(lambda: fobj.read(4096), b""):
        hash.update(chunk)
    if rewind:
        fobj.seek(0)
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
        v = style(varname, fg="cyan", bold=True)
        echo(f"Environment variable {v} is not set.")
        secho("Aborting", fg="red", bold=True)
        return
    p = Path(env)
    assert p.is_dir()
    return p
