from click import command, argument, File
from json import load
from sys import stdin
from time import time
from sparrow.core.plugins import SparrowPlugin
from sparrow.core.context import get_database
from macrostrat.database import on_conflict
from sparrow.logs import setup_stderr_logs


@command(name="validate-data")
@argument("model_name", type=str)
def validate_data(model_name):
    """Try to import data into the database to see if errors are raised.
    Pipe JSON into this command's stdin to see if the import will be successful.
    """
    setup_stderr_logs()
    setup_stderr_logs("sqlalchemy.engine")
    db = get_database()
    data = load(stdin)
    # In some cases, we might have data in the "data" key
    # NOTE: this is likely a bad assumption in many cases, probably
    schema = getattr(db.interface, model_name)()
    t0 = time()
    with on_conflict("do-nothing"):
        res = schema.load(data, session=db.session)
        db.session.add(res)
    t_delta = time() - t0
    print(f"Elapsed time: {t_delta:.2f} seconds")


class DataValidationPlugin(SparrowPlugin):
    """Plugin that enables data validation on input schemas"""

    name = "data-validation-cli"

    def on_setup_cli(self, cli):
        cli.add_command(validate_data)
