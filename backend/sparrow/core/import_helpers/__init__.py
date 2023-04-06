from .util import md5hash, SparrowImportError, get_data_directory, get_file_object
from .importer import BaseImporter
from ..plugins import SparrowCorePlugin

from sparrow.loader import InterfaceCollection


class InterfacePlugin(SparrowCorePlugin):
    name = "schema-interface"

    def on_database_ready(self, db):
        iface = InterfaceCollection(db.model)
        db.interface = iface

    def on_setup_cli(self, cli):
        from .cli import show_interface

        cli.add_command(show_interface)
