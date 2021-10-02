import json
from os import path
from itertools import groupby

# import keepachangelog
from packaging.version import Version, InvalidVersion
from ..util import SparrowCommandError, console
from .util import check_version_exists, remove_postrelease


def _check_version_not_exists(version):
    try:
        assert not check_version_exists(version)
    except AssertionError:
        raise SparrowCommandError(f"Version {version} already exists.")


def check_release_validity(version, clean_version=False):
    """Check the validity of release information stored in the codebase"""
    try:
        spec = Version(version)
    except InvalidVersion:
        raise SparrowCommandError(
            f"Version specifier [cyan bold]{version}[/cyan bold] is invalid."
        )

    _check_version_not_exists(version)
    post_base = remove_postrelease(version)

    # Clean version to PEP440 shortened version, if applicable:
    cleaned_version = str(spec)
    if cleaned_version != version and clean_version:
        console.print(
            f"Shortening [cyan bold]{version}[/cyan bold] to [cyan bold]{cleaned_version}[/cyan bold]"
        )
        version = cleaned_version
        _check_version_not_exists(version)

    pre_base = spec.base_version
    cleaned_post_base = remove_postrelease(cleaned_version)

    if spec.is_prerelease and spec.pre is not None:
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

    if spec.is_postrelease and not (
        check_version_exists(post_base) or check_version_exists(cleaned_post_base)
    ):
        raise SparrowCommandError(
            f"Cannot create a postrelease for nonexistent version {post_base}."
        )
    console.print()
    return version
