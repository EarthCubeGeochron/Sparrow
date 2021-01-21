import click
from ..context import SparrowConfig
from ..meta import __version__


@click.command("info")
@click.pass_context
def sparrow_info(ctx):
    """Show information about this Sparrow installation"""
    cfg = ctx.find_object(SparrowConfig)

    print("Command-line app:")
    if cfg.is_frozen:
        print(f"  Frozen with PyInstaller: {cfg.cli_root}")
    else:
        print(f"  Source installation: {cfg.SPARROW_PATH}")
    print(f"  Version: {__version__}")
