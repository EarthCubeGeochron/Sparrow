"""
This module houses utility functions that are shared between Sparrow's
core and command-line interface.
"""
from os import path
from .logs import setup_stderr_logs, get_logger
from .shell import cmd


def relative_path(base, *parts):
    if not path.isdir(base):
        base = path.dirname(base)
    return path.join(base, *parts)