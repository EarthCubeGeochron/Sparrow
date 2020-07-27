#!/usr/bin/env python3
# The sparrow command-line application is designed to run locally on user machines,
# rather than in Docker. This gives it the ability to more easily integrate with
# the base system.

import sys
import re
import click
from click import echo, style, secho
from os import environ, getcwd, chdir, path
from pathlib import Path
from typing import Optional
from rich import print
from rich.console import Console
from envbash import load_envbash
from .help import echo_help
from .util import cmd, compose, container_is_running
from .test import sparrow_test
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


def find_subcommand(directories, name):
    if name is None:
        return None
    for dir in directories:
        fn = dir / ("sparrow-" + name)
        if fn.is_file():
            return str(fn)


@click.command(
    "sparrow", context_settings=dict(ignore_unknown_options=True, help_option_names=[],)
)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cli(ctx, args):
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

    bin_directories = setup_command_path()
    prepare_docker_environment()

    rest = []
    try:
        (subcommand, *rest) = args
    except ValueError:
        subcommand = "--help"

    if subcommand in ["--help", "help"]:
        echo_help(*bin_directories)
        sys.exit(0)

    if subcommand == "compose":
        return compose(*rest)

    if subcommand == "test":
        return sparrow_test(*rest)

    _command = find_subcommand(bin_directories, subcommand)

    if _command is None:
        # Run a command against sparrow within a docker container
        # This exec/run switch is added because there are apparently
        # database/locking issues caused by spinning up arbitrary
        # backend containers when containers are already running.
        # TODO: We need a better understanding of best practices here.
        if container_is_running("backend"):
            return compose("--log-level ERROR exec backend sparrow", *args)
        else:
            return compose("--log-level ERROR run --rm backend sparrow", *args)
    else:
        return cmd(_command, *rest)
