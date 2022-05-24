from os import chdir
import click
from click.decorators import argument
from rich import print
from ..util.shell import cmd
from ..config import SparrowConfig
from ..meta import __version__


@click.command("update")
@click.pass_context
@argument("version", default=None, required=False)
def sparrow_update(ctx, version):
    """Show information about this Sparrow installation"""
    cfg = ctx.find_object(SparrowConfig)
    if cfg.bundle_dir is None:
        print(f"Sparrow is installed from source. Updating locally.")
        chdir(cfg.SPARROW_PATH)
        cmd("make install-dev")
        return
    fn = str(cfg.SPARROW_PATH / "get-sparrow.sh")
    if version is None:
        cmd(fn)
    else:
        cmd(fn, version)
