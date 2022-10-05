from os import chdir
import click
from click.decorators import argument, option
from rich import print
from ..util.shell import cmd
from ..config import SparrowConfig
from ..meta import __version__


@click.command("update")
@click.pass_context
@argument("version", default=None, required=False)
@option("--prerelease", is_flag=True, default=False)
def sparrow_update(ctx, version, prerelease=False):
    """Update Sparrow to the latest version"""
    cfg = ctx.find_object(SparrowConfig)
    if cfg.bundle_dir is None:
        print(f"Sparrow is installed from source.")
        print(f"Updating the local installation at [cyan]{cfg.SPARROW_PATH}[/cyan]")
        chdir(cfg.SPARROW_PATH)
        cmd("make install-dev")
        return
    fn = str(cfg.SPARROW_PATH / "get-sparrow.sh")
    if version is None:
        cmd(fn, "--prerelease" if prerelease else "")
    else:
        cmd(fn, version)


@click.command("upgrade", hidden=True)
@click.pass_context
def sparrow_upgrade(ctx):
    """Update Sparrow to the latest version"""
    print("[cyan]sparrow upgrade[/cyan] is a synonym for [cyan]sparrow update[/cyan]")
    ctx.invoke(sparrow_update)
