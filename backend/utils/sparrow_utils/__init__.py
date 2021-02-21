"""
This module houses utility functions that are shared between Sparrow's
core and command-line interface.
"""

from .logs import setup_stderr_logs, get_logger
from .shell import cmd