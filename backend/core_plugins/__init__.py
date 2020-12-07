# flake8: noqa
from .earthchem_vocabulary import EarthChemVocabularyPlugin
from .location_names import LocationNamesPlugin
from .destructive_operations import DestructiveOperationsPlugin
from .project_edit import ProjectEditPlugin
# These should only be run by labs that enable them
from .versioning import VersioningPlugin
from .import_data import ImportDataPlugin
from .init_sql import InitSQLPlugin
from sparrow.ext.pychron import PyChronImportPlugin
