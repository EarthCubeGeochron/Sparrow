import click
from ..cli.util import with_app


@click.command(name="show-interface")
@click.argument("model", type=click.STRING)
@click.option("--depth", "-d", type=int, default=0)
@with_app
def show_interface(app, model, depth=0):
    """
    Show the import interface for a database model.
    """
    # `using` is related to this issue:
    # https://github.com/ipython/ipython/issues/11523
    m = getattr(app.database.interface, model)
    m().pretty_print(nested=depth)
