import os
from os import path
from pathlib import Path
from contextlib import contextmanager
from subprocess import run as _run
from shlex import split
from sparrow.utils import relative_path


@contextmanager
def working_directory(pathname, *args):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    fn = path.realpath(pathname)
    if not path.isdir(fn):
        fn = path.dirname(fn)
    fn = path.abspath(path.join(fn, *args))
    os.chdir(fn)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def get_qualified_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + "." + obj.__class__.__name__


def run(*v, **kwargs):
    val = " ".join(v)
    return _run(split(val), **kwargs)
