import click
import json
from click import argument, option
from os import chdir, path
from shlex import quote

# import keepachangelog
from ..config import SparrowConfig
from ..util import SparrowCommandError, cmd, console
from .util import check_output
from .check_validity import check_release_validity
from .check_consistency import check_consistency


def write_version_info(version):
    backend_meta = path.join("backend", "sparrow", "core", "meta.py")
    with open(backend_meta, "w") as f:
        f.write(f'__version__ = "{version}"\n')

    version_file = "sparrow-version.json"
    info = json.load(open(version_file, "r"))
    info["core"] = version
    json.dump(info, open(version_file, "w"), indent=2)
    return (backend_meta, version_file)


@click.command(name="create-release")
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

    if version.startswith("v"):
        version = version[1:]

    console.print(f"\nCreating release {version}", style="green bold")

    version = check_release_validity(version)

    output = check_output("git status --short")
    if bool(output) and not force:
        raise SparrowCommandError(
            "Refusing to create a release with a dirty working directory. "
            "Commit your changes or rerun with [cyan]--force[/cyan] to continue.",
            details=output,
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
    res = cmd("git tag -a", tag_name, "-m", quote(commit_info))
    if res.returncode != 0:
        raise SparrowCommandError(
            f"Could not create tag [green bold]{tag_name}", details=res.stderr
        )

    check_consistency(tag_name)

    console.print("[green bold]Successfully created release")

    if push:
        console.print("\n[green bold]Pushing changes")
        cmd("git push -u origin HEAD")
    else:
        console.print("Finalize your release using [cyan]git push[/cyan].")


@click.command(name="check-version")
@argument("version", required=False, default=None)
@option("--exact", is_flag=True, help="Check for exact version", default=False)
@click.pass_context
def check_version(ctx, version=None, exact=False):
    """Check that version information is consistent throughout the codebase."""
    cfg = ctx.find_object(SparrowConfig)
    if not cfg.is_source_install():
        raise SparrowCommandError(
            "Only source installations of Sparrow contain versioning information."
        )
    root_dir = cfg.SPARROW_PATH
    # We should bail here if we are running a bundled Sparrow...
    chdir(root_dir)
    check_consistency(tag_name=version, exact=exact)
