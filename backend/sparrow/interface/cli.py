import click
from sparrow.cli.util import with_config, construct_app

@click.command(name='show-interface')
@click.argument('model', type=click.STRING)
@click.option('--depth','-d', type=int, default=0)
@with_config
def show_interface(cfg, model, depth=0):
    """
    Show the import interface for a database model.
    """
    app, db = construct_app(cfg)

    with app.app_context():
        # `using` is related to this issue:
        # https://github.com/ipython/ipython/issues/11523
        m = getattr(app.interface, model)
        m().pretty_print(nested=depth)
