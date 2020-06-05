#!/usr/bin/env python3
# The sparrow command-line application is designed to run locally on user machines.

import sys
from click import echo, style, secho
from os import environ, getcwd
from pathlib import Path
from typing import Optional
from rich import print
import sys

def find_config_file(dir: Path) -> Optional[Path]:
    for folder in (dir, *dir.parents):
        pth = folder/"sparrow-config.sh"
        if pth.is_file():
            return pth


def get_config() -> Optional[Path]:
    # Get configuration from existing environment variable
    __config = environ.get("SPARROW_CONFIG")
    if __config is None:
        return None
    return Path(__config)


def echo_help(directories):
    echo("Help!")

def cli():
    wd = getcwd()
    environ['SPARROW_WORKDIR'] = wd
    here = Path(wd)

    sparrow_config = get_config()

    if sparrow_config is None:
        # Search for configuration file if it isn't already defined
        sparrow_config = find_config_file(here)

    if sparrow_config is None:
        echo("No configuration file found. Running using default values.", err=True)
    echo(str(sparrow_config))
    environ['SPARROW_CONFIG'] = str(sparrow_config)

    # Check if this script is part of a source
    # installation. If so, set SPARROW_PATH accordingly
    is_frozen = getattr( sys, 'frozen', False )
    if "SPARROW_PATH" not in environ:
        this_exe = Path(__file__).resolve()
        if not is_frozen:
            path = this_exe.parent.parent
            environ['SPARROW_PATH'] = str(path)

    bin_directories = []

    if 'SPARROW_PATH' in environ:
        bin = Path(environ['SPARROW_PATH'])/'bin'
        bin_directories.append(bin)
    else:
        secho("A local Sparrow source directory could not be automatically found. "
              "Running without a local installation is not yet supported. "
              "Please set SPARROW_PATH to the location of the cloned Sparrow repository.", fg='red')
        sys.exit(1)
    echo(environ["SPARROW_PATH"])

    # ENVIRONMENT VARIABLE DEFAULTS
    # Set variables that might not be created in the config file
    # to default values
    # NOTE: much of this has been moved to `docker-compose.yaml`
    environ.setdefault("SPARROW_BASE_URL", "/")
    environ.setdefault("SPARROW_LAB_NAME", "My Lab")


    # Make sure all internal commands can be referenced by name from
    # within Sparrow (even if `sparrow` command itself isn't on the PATH)
    __cmd = environ.get("SPARROW_COMMANDS")
    if __cmd is not None:
        bin_directories += Path(__cmd)

    # Add location of Sparrow commands to path
    __added_path_dirs = [str(i) for i in bin_directories]
    environ['PATH'] = ":".join([*__added_path_dirs, environ["PATH"]])

    if environ.get("SPARROW_SECRET_KEY") is None:
        echo("You "+style("must")+" set SPARROW_SECRET_KEY. Exiting...")
        sys.exit(1)

    try:
        subcommand = sys.argv[1]
    except IndexError:
        subcommand = "--help"

    if subcommand in ["--help", "help"]:
        echo_help(bin_directories)
        sys.exit(0)

    echo("Hello, world!")

if __name__ == '__main__':
    cli()
