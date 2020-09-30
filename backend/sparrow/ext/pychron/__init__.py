from click import command
from sparrow.plugins.base import SparrowPlugin

from .json_transformer import PyChronJSONImporter


@command(name="import-pychron")
def pychron_import_command():
    """Import PyChron Interpreted Age files."""
    print("Hello, world...")


class PyChronImportPlugin(SparrowPlugin):
    name = "pychron-importer"

    def on_setup_cli(self, cli):
        cli.add_command(pychron_import_command)
