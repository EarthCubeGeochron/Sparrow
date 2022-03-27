import typing
from dataclasses import dataclass
from os import environ
from macrostrat.core_utils.shell import cmd
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version


@dataclass
class SparrowVersionMatch:
    is_match: bool
    desired: str
    available: str
    uses_git: bool


def get_commit(cfg, match="HEAD"):
    rev = cmd(
        "git rev-parse --short",
        match + "^{commit}",
        cwd=cfg.SPARROW_PATH,
        capture_output=True,
    )
    return rev.stdout.decode("utf-8").strip()


def test_git_version(cfg, required_version) -> typing.Union[SparrowVersionMatch, None]:
    # Fall back to git-based version string parsing...
    if cfg.is_frozen and not cfg.path_provided:
        rev = cfg.git_revision()["revision"].removesuffix("-dirty")
    else:
        rev = get_commit(cfg, "HEAD")

    match_rev = get_commit(cfg, required_version)
    # Could print a cautionary note if we are using a branch name or HEAD...
    return SparrowVersionMatch(
        is_match=rev == match_rev,
        desired=required_version,
        available=rev,
        uses_git=True,
    )


def test_version(cfg) -> typing.Union[SparrowVersionMatch, None]:
    # Test version string against requested version of SPARROW
    # https://www.python.org/dev/peps/pep-0440/
    # https://www.python.org/dev/peps/pep-0440/#version-specifiers
    # We should make this handle git commits and tags as well...
    required_version = environ.get("SPARROW_VERSION", None)
    if required_version is None:
        return

    # We should maybe admonish the user here that specifying a
    # SPARROW_VERSION or SPARROW_PATH is recommended...

    try:
        spec = SpecifierSet(required_version, prereleases=True)
    except InvalidSpecifier:
        # We fall back to testing git commit versions
        return test_git_version(cfg, required_version)

    actual_version = Version(cfg.find_sparrow_version())

    return SparrowVersionMatch(
        is_match=actual_version in spec,
        desired=str(spec),
        available=str(actual_version),
        uses_git=False,
    )
