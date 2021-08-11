"""
A plugin for destructive operations to the Sparrow database.
"""

import sparrow
from sparrow.util import relative_path


@sparrow.task(name="remove-analytical-data", destructive=True)
def remove_analytical_data():
    """Remove all analytical data from the Sparrow database"""
    db = sparrow.get_database()
    qfile = relative_path(__file__, "remove-analytical-data.sql")
    db.exec_sql(qfile)
