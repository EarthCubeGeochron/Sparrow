"""
A plugin for destructive operations to the Sparrow database.
"""

from os.path import join, realpath, dirname
from click import command
from sparrow.plugins import SparrowCorePlugin
from sparrow.cli.util import with_database
from sparrow.util import relative_path


@command(name="remove-analytical-data")
@with_database
def remove_analytical_data(db):
    qfile = relative_path(__file__, 'remove-analytical-data.sql')
    db.exec_sql(qfile)


# Basic shim plugin that loads an external CLI
class DestructiveOperationsPlugin(SparrowCorePlugin):
    name = "destructive-operations"

    def on_setup_cli(self, cli):
        cli.add_command(remove_analytical_data)
