import click
from ..context import SparrowConfig
from ..meta import __version__
from json import load


def sparrow_core_version(cfg):
    try:
        return cfg.find_sparrow_version()
    except Exception:
        return "<= 1.6.0 (version information could not be assembled)"


@click.command("info")
@click.pass_context
def sparrow_info(ctx):
    """Show information about this Sparrow installation"""
    cfg = ctx.find_object(SparrowConfig)
    rev = cfg.git_revision()["revision"]

    print("Command-line interface:")
    if cfg.is_frozen:
        print(f"  Bundled with PyInstaller: {cfg.bundle_dir}")
    else:
        print(f"  Source installation: {cfg.SPARROW_PATH}")
    print(f"  Version: {__version__}")
    print(f"  Git revision: {rev}")
    print("")

    print("Core application:")
    if cfg.path_provided:
        print(f"  Overridden from user configuration")
    if not cfg.path_provided and cfg.is_frozen:
        print(f"  Bundled with PyInstaller")
    else:
        print(f"  Source installation: {cfg.SPARROW_PATH}")
    print(f"  Version: {sparrow_core_version(cfg)}")
    print(f"  Git revision: {rev}")
