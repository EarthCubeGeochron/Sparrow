"""
A plugin for destructive operations to the Sparrow database.
"""

from macrostrat.utils import relative_path

from sparrow.core import get_database, task


@task(name="remove-analytical-data", destructive=True)
def remove_analytical_data():
    """Remove all analytical data from the Sparrow database"""
    db = get_database()
    qfile = relative_path(__file__, "remove-analytical-data.sql")
    db.run_sql(qfile)
