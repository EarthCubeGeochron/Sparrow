import sys
import click
import typing
from click import echo, make_pass_decorator
from click_default_group import DefaultGroup
from os import environ, getcwd, chdir
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from rich.console import Console
from envbash import load_envbash
from .env import prepare_docker_environment, setup_command_path


def find_config_file(dir: Path) -> Optional[Path]:
    for folder in (dir, *dir.parents):
        pth = folder / "sparrow-config.sh"
        if pth.is_file():
            return pth


def get_config() -> Optional[Path]:
    # Get configuration from existing environment variable
    __config = environ.get("SPARROW_CONFIG")
    __config_unset = environ.get("_SPARROW_CONFIG_UNSET", "0") == "1"
    if __config is None or __config_unset:
        return None
    return Path(__config)


console = Console(highlight=True)


@dataclass
class SparrowConfig:
    bin_directories: typing.List[Path]


@click.group(name="sparrow", cls=DefaultGroup, default="main", default_if_no_args=True)
@click.pass_context
def cli(ctx):
    """Startup function that sets configuration environment variables. Much of the
    structure of this is inherited from when the application was bootstrapped by a
    `zsh` script.
    """
    environ["SPARROW_WORKDIR"] = getcwd()
    here = Path(environ["SPARROW_WORKDIR"])

    sparrow_config = get_config()

    if sparrow_config is None:
        # Search for configuration file if it isn't already defined
        sparrow_config = find_config_file(here)

    if sparrow_config is None:
        echo("No configuration file found. Running using default values.", err=True)
        environ["_SPARROW_CONFIG_UNSET"] = "1"
    else:
        environ["SPARROW_CONFIG"] = str(sparrow_config)
        environ["SPARROW_CONFIG_DIR"] = str(sparrow_config.parent)

    _config_sourced = environ.get("_SPARROW_CONFIG_SOURCED", "0") == "1"

    if sparrow_config is not None and not _config_sourced:
        chdir(environ["SPARROW_CONFIG_DIR"])
        # This requires bash to be available on the platform, which
        # might be a problem for Windows/WSL.
        load_envbash(environ["SPARROW_CONFIG"])
        # Change back to original working directory
        chdir(environ["SPARROW_WORKDIR"])
        environ["_SPARROW_CONFIG_SOURCED"] = "1"

    # Check if this script is part of a source
    # installation. If so, set SPARROW_PATH accordingly
    is_frozen = getattr(sys, "frozen", False)
    if "SPARROW_PATH" not in environ:
        this_exe = Path(__file__).resolve()
        if not is_frozen:
            pth = this_exe.parent.parent.parent
            environ["SPARROW_PATH"] = str(pth)

    cfg = SparrowConfig(bin_directories=setup_command_path())
    ctx.obj = cfg
    prepare_docker_environment()
