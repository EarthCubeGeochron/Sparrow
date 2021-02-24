import sys
import click
from click import echo, secho, style
from click_default_group import DefaultGroup
from sparrow_utils.logs import setup_stderr_logs
from os import environ, getcwd, chdir
from pathlib import Path
from typing import Optional
from rich.console import Console
from .config_loader import load_config
from .env import prepare_docker_environment, setup_command_path
from .exc import SparrowCommandError
from .context import SparrowConfig
from packaging.specifiers import SpecifierSet
from packaging.version import Version


class SparrowDefaultCommand(DefaultGroup):
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except SparrowCommandError as exc:
            prefix = str(type(exc).__name__) + ": "
            echo(
                "\n" + style(prefix, bold=True, fg="red") + style(str(exc), fg="red"),
                err=True,
            )
            details = getattr(exc, "details", None)
            if details is not None:
                secho(details, dim=True)
            # Maybe we should reraise only if debug is set?
            raise exc


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


@click.group(
    name="sparrow", cls=SparrowDefaultCommand, default="main", default_if_no_args=True
)
@click.option("--verbose/--no-verbose", is_flag=True, default=False)
@click.pass_context
def cli(ctx, verbose=False):
    """Startup function that sets configuration environment variables. Much of the
    structure of this is inherited from when the application was bootstrapped by a
    `zsh` script.
    """
    if verbose:
        setup_stderr_logs("sparrow_cli")

    environ["SPARROW_WORKDIR"] = getcwd()
    here = Path(environ["SPARROW_WORKDIR"])

    sparrow_config = get_config()

    if sparrow_config is None:
        # Search for configuration file if it isn't already defined
        sparrow_config = find_config_file(here)

    if sparrow_config is None:
        # echo("No configuration file found. Running using default values.", err=True)
        environ["_SPARROW_CONFIG_UNSET"] = "1"
    else:
        environ["SPARROW_CONFIG"] = str(sparrow_config)
        environ["SPARROW_CONFIG_DIR"] = str(sparrow_config.parent)

    _config_sourced = environ.get("_SPARROW_CONFIG_SOURCED", "0") == "1"

    if sparrow_config is not None and not _config_sourced:
        chdir(environ["SPARROW_CONFIG_DIR"])
        # This requires bash to be available on the platform, which
        # might be a problem for Windows/WSL.
        load_config(environ["SPARROW_CONFIG"])
        # Change back to original working directory
        chdir(environ["SPARROW_WORKDIR"])
        environ["_SPARROW_CONFIG_SOURCED"] = "1"

    # First steps towards some much more object-oriented configuration
    ctx.obj = SparrowConfig()

    # Test version string against requested version of SPARROW
    # https://www.python.org/dev/peps/pep-0440/
    # We should make this handle git commits and tags as well...
    required_version = environ.get("SPARROW_VERSION", None)
    if required_version is not None:
        spec = SpecifierSet(required_version, prereleases=True)
        actual_version = Version(ctx.obj.find_sparrow_version())
        if not actual_version in spec:
            raise SparrowCommandError(
                f"Sparrow version {actual_version} is not in {spec}"
            )

    prepare_docker_environment()
