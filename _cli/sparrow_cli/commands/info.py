import click
from ..context import SparrowConfig


@click.command("info")
@click.pass_context
def sparrow_info(ctx):
    """Show information about this Sparrow installation"""
    cfg = ctx.find_object(SparrowConfig)

    print("Command-line app: ", end="")
    if cfg.is_frozen:
        print(f"frozen with PyInstaller to {cfg.cli_root}")
    else:
        print(f"source build at {cfg.SPARROW_PATH}")
