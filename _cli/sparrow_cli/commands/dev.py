from click import group, secho, option
from os import environ, path, chdir
from runpy import run_path
from subprocess import run
import json
from ..group import CommandGroup
from ..util import compose

# Commands inherited from earlier shell version of CLI.
shell_commands = {
    "graph": "Graph the git commit history of the Sparrow repository",
    "local": "Run sparrow with a locally-installed frontend (this can be less resource-intensive)",
}


@group(name="dev", cls=CommandGroup)
def sparrow_dev():
    pass


for k, v in shell_commands.items():
    sparrow_dev.add_shell_command(k, v, prefix="sparrow-dev-")


@sparrow_dev.command(name="reload")
def dev_reload():
    """Reload the web browser when the app is in development mode"""
    compose("exec frontend /app/node_modules/.bin/browser-sync reload")


def _sync_version_info():
    root_dir = environ.get("SPARROW_PATH")
    # We should bail here if we are running a bundled Sparrow...
    chdir(root_dir)
    meta = run_path(path.join("backend", "sparrow", "meta.py"))

    version_file = "sparrow-version.json"
    info = json.load(open(version_file, "r"))
    if info["core"] == meta["__version__"]:
        return

    secho("Updating version information", fg="green", err=True)
    info["core"] = meta["__version__"]
    json.dump(info, open(version_file, "w"), indent=2)
    run(["git", "add", "sparrow-version.json"])


@sparrow_dev.command(name="sync-version-info")
def sync_version_info():
    _sync_version_info()


@sparrow_dev.command(name="clear-cache")
def clear_cache():
    """Clear caches used by the command-line application"""
    from ..help.backend import cli_cache_file

    cli_cache_file().unlink()


@sparrow_dev.command(name="create-release")
def create_release():
    """Create a Sparrow release."""
    root_dir = environ.get("SPARROW_PATH")
    _sync_version_info()
    res = run(["git", "status"])
    print(res)
