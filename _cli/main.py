#!/usr/bin/env python3
# The sparrow command-line application is designed to run locally on user machines,
# rather than in Docker. This gives it the ability to more easily integrate with
# the base system.

import sys
import re
from click import echo, style, secho
from os import environ, getcwd, chdir, path
from pathlib import Path
from typing import Optional
from rich import print
from rich.console import Console
from subprocess import run, PIPE
from shlex import split
from envbash import load_envbash


def cmd(*v, **kwargs):
    val = " ".join(v)
    return run(split(val), **kwargs)


def find_config_file(dir: Path) -> Optional[Path]:
    for folder in (dir, *dir.parents):
        pth = folder/"sparrow-config.sh"
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

desc_regex = re.compile("^#\s+Description:\s+(.+)$")
def get_description(script):
    with open(script, 'r') as f:
        for line in f:
            m = desc_regex.match(line)
            if m is not None:
                v = m.group(1)
                return re.sub('`(.*?)`','[cyan]\\1[/cyan]',v)
    return ""

def cmd_help(title, directory: Path):
    echo("", err=True)
    print(title+":", file=sys.stderr)

    # Add sparrow compose help separately
    # TODO: integrate into `click`
    echo("  {0:24}".format('compose'), err=True, nl=False)
    console.print("Alias to [cyan]docker-compose[/cyan] that respects [cyan]sparrow[/cyan] config", highlight=True)


    for f in directory.iterdir():
        if not f.is_file():
            continue
        name = f.stem
        prefix = "sparrow-"
        if not name.startswith(prefix):
            continue

        echo("  {0:24}".format(name[len(prefix):]), err=True, nl=False)
        desc = get_description(f)
        console.print(desc, highlight=True)

def compose(*args, **kwargs):
    base = environ['SPARROW_PATH']
    main = path.join(base, "docker-compose.yaml")
    overrides = environ.get("SPARROW_COMPOSE_OVERRIDES", "")
    chdir(base)
    return cmd("docker-compose", "-f", main, overrides, *args, **kwargs)

def echo_help(core_commands=None, user_commands=None):
    echo("Usage: "+style("sparrow", bold=True)+" [options] <command> [args]...", err=True)
    echo("", err=True)
    echo("Config: "+style(environ['SPARROW_CONFIG'], fg='cyan'), err=True)
    echo("Lab: "+style(environ['SPARROW_LAB_NAME'], fg='cyan', bold=True), err=True)
    out = compose("run --no-deps backend sparrow", shell=True, stdout=PIPE)
    if out.returncode != 0:
        echo(out.stderr, err=True)
    else:
        echo(b"\n".join(out.stdout.splitlines()[1:]), err=True)

    if user_commands is not None:
        lab_name = environ.get("SPARROW_LAB_NAME", "Lab-specific")
        cmd_help("[underline]"+lab_name+"[/underline] commands", user_commands)

    cmd_help("Container management commands", core_commands)


def container_is_running(name):
    return False

def find_subcommand(directories, name):
    if name is None:
        return None
    for dir in directories:
        fn = dir/("sparrow-"+name)
        if fn.is_file():
            return str(fn)


def cli():
    environ['SPARROW_WORKDIR'] = getcwd()
    here = Path(environ['SPARROW_WORKDIR'])

    sparrow_config = get_config()

    if sparrow_config is None:
        # Search for configuration file if it isn't already defined
        sparrow_config = find_config_file(here)

    if sparrow_config is None:
        echo("No configuration file found. Running using default values.", err=True)
        environ['_SPARROW_CONFIG_UNSET'] = '1'
    else:
        environ['SPARROW_CONFIG'] = str(sparrow_config)
        environ['SPARROW_CONFIG_DIR'] = str(sparrow_config.parent)

    _config_sourced = environ.get("_SPARROW_CONFIG_SOURCED", "0") == "1"

    if sparrow_config is not None and not _config_sourced:
        chdir(environ['SPARROW_CONFIG_DIR'])
        # This requires bash to be available on the platform, which
        # might be a problem for Windows/WSL.
        load_envbash(environ['SPARROW_CONFIG'])
        # Change back to original working directory
        chdir(environ['SPARROW_WORKDIR'])
        environ["_SPARROW_CONFIG_SOURCED"] = "1"

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
        secho("Sparrow could not automatically find a the source directory. "
              "Running without a local installation is not yet supported. "
              "Please set SPARROW_PATH to the location of the cloned Sparrow repository.", fg='red')
        sys.exit(1)

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
        bin_directories.append(Path(__cmd))

    # Add location of Sparrow commands to path
    __added_path_dirs = [str(i) for i in bin_directories]
    environ['PATH'] = ":".join([*__added_path_dirs, environ["PATH"]])

    if environ.get("SPARROW_SECRET_KEY") is None:
        print("[red]You [underline]must[/underline] set [bold]SPARROW_SECRET_KEY[/bold]. Exiting...")
        sys.exit(1)

    args = []
    try:
        (subcommand, *args) = sys.argv[1:]
    except ValueError:
        subcommand = "--help"

    if subcommand in ["--help", "help"]:
        echo_help(*bin_directories)
        sys.exit(0)

    if subcommand == 'compose':
        return compose(*args)

    _command = find_subcommand(bin_directories, subcommand)

    if _command is None:
        # Run a command against sparrow within a docker container
        # This exec/run switch is added because there are apparently
        # database/locking issues caused by spinning up arbitrary
        # backend containers when containers are already running.
        # TODO: We need a better understanding of best practices here.
        if container_is_running("backend"):
            compose("--log-level ERROR exec backend sparrow", *args)
        else:
            compose("--log-level ERROR run --rm backend sparrow", *args)
    else:
        cmd(_command, *args)

if __name__ == '__main__':
    cli()
