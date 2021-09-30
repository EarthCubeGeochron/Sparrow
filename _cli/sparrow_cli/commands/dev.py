import click
from rich import print
from click import group, secho, argument, option
from os import environ, path, chdir
from runpy import run_path
from subprocess import run
import json
import re
from ..config import SparrowConfig
from ..util import SparrowCommandError, CommandGroup, compose, cmd

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


def check_version_allowed(version, message="Trying to create a duplicate release."):
    tag_name = "v" + version
    res = cmd("git tag -l", tag_name, capture_output=True)
    if bool(res.stdout.strip()):
        raise SparrowCommandError(
            message, details=f"Tag [cyan]{tag_name}[/cyan] already exists"
        )
    return tag_name


@sparrow_dev.command(name="create-release")
@argument("version")
@option(
    "--force", is_flag=True, help="Force release when git configuration is not clean"
)
@click.pass_context
def create_release(ctx, version, force=False):
    """Show information about this Sparrow installation"""
    cfg = ctx.find_object(SparrowConfig)
    if not cfg.is_source_install():
        raise SparrowCommandError(
            "Sparrow versions cannot be created from the bundled version."
        )
    root_dir = cfg.SPARROW_PATH
    # We should bail here if we are running a bundled Sparrow...
    chdir(root_dir)

    match = re.match(r"^((\d+\.\d+\.\d+)(\.([a-z]*\d+))?([-\.](\d+))?)$", version)
    if match is None:
        raise SparrowCommandError(
            "Invalid version string",
            details="Version must be in a format like 1.2.3[.[abc]4][(-.)5]",
        )

    res = cmd("git status --short", capture_output=True)
    if bool(res.stdout.strip()) and not force:
        raise SparrowCommandError(
            "Refusing to create a release with a dirty working directory. Commit your changes or rerun with [cyan]--force[/cyan] to continue.",
            details=res.stdout,
        )

    if not force:
        res = cmd("git pull --all")
        if res.returncode != 0:
            raise SparrowCommandError(
                "Could not pull from remote repositories. Rerun with [cyan]--force[/cyan] to skip this step.",
                details=res.stderr,
            )

    print(f"[green]Creating release for version [bold]{version}")
    is_prerelease = match.group(4) is not None
    core_version = match.group(2)
    if is_prerelease:
        print(f"This is a prerelease for version [bold]{core_version}")
        check_version_allowed(
            core_version, "Cannot create a prerelease for an existing version"
        )
    print()

    tag_name = check_version_allowed(version)

    print("Syncing version info to repository files.")
    backend_meta = path.join("backend", "sparrow", "meta.py")
    with open(backend_meta, "w") as f:
        f.write(f'__version__ = "{version}"\n')

    version_file = "sparrow-version.json"
    info = json.load(open(version_file, "r"))
    if info["core"] != version:
        info["core"] = version
        json.dump(info, open(version_file, "w"), indent=2)

    print("\n[green bold]Committing and tagging release")

    cmd("git add", backend_meta, "sparrow-version.json")
    commit_info = f"'Version {version}'"
    cmd("git commit -m", commit_info)

    res = cmd("git tag -a", tag_name, "-m", commit_info)
    if res.returncode != 0:
        raise SparrowCommandError(
            f"Could not create tag {tag_name}", details=res.stderr
        )

    print("\n[green bold]Pushing changes")
    cmd("git push")


@sparrow_dev.command(name="clear-cache")
def clear_cache():
    """Clear caches used by the command-line application"""
    from ..help.options_cache import cli_cache_file

    cli_cache_file().unlink()
