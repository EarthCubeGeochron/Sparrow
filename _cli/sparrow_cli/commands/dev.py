from sparrow_cli.config import version_info
import click
from rich import print
from rich.console import Console
from click import group, secho, argument, option
from os import path, chdir
from shlex import quote
from runpy import run_path
from subprocess import run
import json

# import keepachangelog
from packaging.version import Version, InvalidVersion
from ..config import SparrowConfig
from ..util import (
    SparrowCommandError,
    CommandGroup,
    compose,
    cmd,
    console,
    exec_sparrow,
)

console = Console(highlight=False)


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


def check_version_exists(version):
    tag_name = "v" + version
    res = cmd("git tag -l", tag_name, capture_output=True)
    return bool(res.stdout.strip())


def write_version_info(version):
    backend_meta = path.join("backend", "sparrow", "meta.py")
    with open(backend_meta, "w") as f:
        f.write(f'__version__ = "{version}"\n')

    version_file = "sparrow-version.json"
    info = json.load(open(version_file, "r"))
    info["core"] = version
    json.dump(info, open(version_file, "w"), indent=2)
    return (backend_meta, version_file)


def remove_postrelease(version):
    spec = Version(version)
    while spec.is_postrelease:
        version = version[:-1]
        try:
            spec = Version(version)
        except InvalidVersion:
            pass
    return version


def check_release_validity(version):
    try:
        spec = Version(version)
        assert not check_version_exists(version)
    except InvalidVersion:
        raise SparrowCommandError(f"Version specifier {version} is invalid.")

    except AssertionError:
        raise SparrowCommandError(f"Version {version} already exists.")

    pre_base = spec.base_version
    post_base = remove_postrelease(version)

    if spec.is_prerelease:
        pre = spec.pre
        console.print(
            f"- Prerelease [cyan bold]{pre[0]}{pre[1]}[/cyan bold] for version {pre_base}"
        )
    if spec.is_postrelease:
        console.print(
            f"- Postrelease [cyan bold]{spec.post}[/cyan bold] for version {post_base}"
        )

    if spec.is_prerelease and check_version_exists(pre_base):
        raise SparrowCommandError(
            f"Cannot create a prerelease for existing version {pre_base}."
        )

    if spec.is_postrelease and not check_version_exists(post_base):
        raise SparrowCommandError(
            f"Cannot create a postrelease for non-existant version {post_base}."
        )
    console.print()


@sparrow_dev.command(name="create-release")
@argument("version")
@option(
    "--force",
    is_flag=True,
    help="Force release when git configuration is not clean",
    default=False,
)
@option("--dry-run", is_flag=True, help="Don't make any changes", default=False)
@option("--test/--no-test", is_flag=True, help="Run tests", default=True)
@option(
    "--push/--no-push",
    is_flag=True,
    help="Push release tag when finished",
    default=False,
)
@click.pass_context
def create_release(ctx, version, force=False, dry_run=False, test=True, push=False):
    """Show information about this Sparrow installation"""

    cfg = ctx.find_object(SparrowConfig)
    if not cfg.is_source_install():
        raise SparrowCommandError(
            "Sparrow versions cannot be created from the bundled application."
        )
    root_dir = cfg.SPARROW_PATH
    # We should bail here if we are running a bundled Sparrow...
    chdir(root_dir)

    console.print(f"\nCreating release {version}", style="green bold")

    check_release_validity(version)

    res = cmd("git status --short", capture_output=True)
    if bool(res.stdout.strip()) and not force:
        raise SparrowCommandError(
            "Refusing to create a release with a dirty working directory. "
            "Commit your changes or rerun with [cyan]--force[/cyan] to continue.",
            details=res.stdout,
        )

    if not force:
        # Ensure that we have the latest changes
        res = cmd("git pull --all --ff-only")
        if res.returncode != 0:
            raise SparrowCommandError(
                "Could not pull from remote repositories. Rerun with [cyan]--force[/cyan] to skip this step.",
                details=res.stderr,
            )

    console.print(f"[green bold]Syncing version info to packages.")

    files = write_version_info(version)

    if test:
        console.print("\n[green bold]Running tests")
        res = cmd("sparrow test")
        if res.returncode != 0:
            cmd("git checkout --", *files)
            raise SparrowCommandError(
                "Tests failed. Rerun with [cyan]--no-test[/cyan] to skip this step."
            )

    console.print("\n[green bold]Committing release files")

    commit_info = f"Version {version}"

    if dry_run:
        console.print("\n[green bold]Dry run complete. Potential commit message:")
        console.print(commit_info, style="dim")
        if not force:
            cmd("git checkout HEAD --", *files)
        return

    cmd("git add", *files)
    res = cmd("git commit -m", quote(commit_info))
    if res.returncode != 0:
        cmd("git checkout HEAD --", *files)
        raise SparrowCommandError("Commit not completed successfully")

    console.print("\nTagging release", style="green bold")

    tag_name = "v" + version
    res = cmd("git tag -a", tag_name, f"-m '{commit_info}'")
    if res.returncode != 0:
        raise SparrowCommandError(
            f"Could not create tag [green bold]{tag_name}", details=res.stderr
        )
    console.print("[green bold]Successfully created release")

    if push:
        console.print("\n[green bold]Pushing changes")
        cmd("git push -u origin HEAD")
    else:
        console.print("Finalize your release using [cyan]git push[/cyan].")


@sparrow_dev.command(name="clear-cache")
def clear_cache():
    """Clear caches used by the command-line application"""
    from ..help.options_cache import cli_cache_file

    cli_cache_file().unlink()
