# flake8: noqa
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

from .logs import get_logger
from .app import Sparrow
from .task_manager import sparrow_task
from .plugins import SparrowPlugin
from .database import Database
from .context import get_sparrow_app, get_plugin, get_database

# Support some more concise signatures
get_app = get_sparrow_app
task = sparrow_task

from .meta import __version__
