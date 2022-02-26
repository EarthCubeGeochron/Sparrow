import sys
from os import environ, getcwd, chdir
from envbash import load_envbash
from pathlib import Path
from typing import Optional
from sparrow_utils import get_logger

log = get_logger(__name__)


def envbash_init_hack():
    """
    This is a hack to support the "envbash" module, which allows
    reading environment variables from a bash script.

    Envbash has problems with working under PyInstaller due
    to its use of subprocess.Popen code referencing the python interpreter
    with sys.executable:
    https://pyinstaller.readthedocs.io/en/stable/runtime-information.html#using-sys-executable-and-sys-argv-0
    The sparrow executable is called as the Python interpreter when we are bundled.
    If we don't include this circuit-breaker, the program creates an infinite loop
    of trying to bootstrap.

    SOLUTION: Envbash internally executes a Python one-liner to dump environment variables.
    We execute this code block directly and then bail, mimicking python invoked from the
    command line. The dump-environment command needs to be invoked before any
    further CLI initialization happens.
    NOTE: we could go further and make this a general way to execute Python code,
    but this might have security implications.
    """
    if (
        getattr(sys, "frozen", False)
        and len(sys.argv) == 3
        and sys.argv[1] == "-c"
        and sys.argv[2] == "import os; print(repr(dict(os.environ)))"
    ):
        print(repr(dict(environ)))
        sys.exit(0)


def _load_config_file(cfg: Path):
    log.debug(f"Loading configuration file: {cfg}")
    return load_envbash(str(cfg))


def find_config_file(_dir: Path, filename="sparrow-config.sh") -> Optional[Path]:
    """Find a configuration file searching recursively from the given directory."""
    for folder in (_dir, *_dir.parents):
        pth = folder / filename
        if pth.is_file():
            return pth
    return None


def get_config() -> Optional[Path]:
    # Get configuration from existing environment variable
    __config = environ.get("SPARROW_CONFIG")
    __config_unset = environ.get("_SPARROW_CONFIG_UNSET", "0") == "1"
    if __config is None or __config_unset:
        return None
    return Path(__config)


def load_config_file():
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
        # We denote that we've loaded the configuration file _before_ sourcing it.
        # By doing this, we can actually run `sparrow` subcommands in the config, and
        # we are somewhat more resilient to bad config files.
        environ["_SPARROW_CONFIG_SOURCED"] = "1"
        # Actually source the configuration file as a shell script
        # This requires bash to be available on the platform, which
        # might be a problem for Windows/WSL.
        _load_config_file(sparrow_config)
        # Load the `sparrow-secrets.sh` file if it exists.
        secrets = sparrow_config.with_name("sparrow-secrets.sh")
        if secrets.is_file():
            _load_config_file(secrets)

        # Change back to original working directory
        chdir(environ["SPARROW_WORKDIR"])

    return sparrow_config
