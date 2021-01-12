from click import group
from .group import CommandGroup
from .util import compose
from os import environ, path, chdir
from runpy import run_path
from subprocess import run
import json

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


@sparrow_dev.command(name="sync-version-info")
def sync_version_info():
    root_dir = environ.get("SPARROW_PATH")
    chdir(root_dir)
    meta = run_path(path.join("backend", "sparrow", "meta.py"))

    version_file = "sparrow-version.json"
    info = json.load(open(version_file, "r"))
    if info["core"] == meta["__version__"]:
        return
    info["core"] = meta["__version__"]
    json.dump(info, open(version_file, "w"), indent=2)
    run(["git", "add", "sparrow-version.json"])