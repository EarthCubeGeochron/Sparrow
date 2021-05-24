"""
A plugin for destructive operations to the Sparrow database.
"""

from click import command
from sparrow.plugins import SparrowCorePlugin
from sparrow.util import relative_path
from sparrow.context import get_database


@command(name="remove-analytical-data")
def remove_analytical_data():
    """Remove all analytical data from the Sparrow database"""
    db = get_database()
    qfile = relative_path(__file__, "remove-analytical-data.sql")
    db.exec_sql(qfile)


# Basic shim plugin that loads an external CLI
class DestructiveOperationsPlugin(SparrowCorePlugin):
    name = "destructive-operations"

    def on_setup_cli(self, cli):
        cli.add_command(remove_analytical_data)
