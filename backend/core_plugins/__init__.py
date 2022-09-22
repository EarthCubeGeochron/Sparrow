# flake8: noqa
from .earthchem_vocabulary import EarthChemVocabularyPlugin
from .location_names import LocationNamesPlugin
from .destructive_operations import remove_analytical_data

# These should only be run by labs that enable them
from .versioning import VersioningPlugin
from .init_sql import InitSQLPlugin
from .assets_server import AssetsServerPlugin
from .data_file_server import DataFilePlugin

# We get a "circular import" error doing this...
# from sparrow.ext.pychron import PyChronImportPlugin
