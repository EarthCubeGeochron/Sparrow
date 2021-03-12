import typing
import sys
from dataclasses import dataclass
from pathlib import Path
from os import environ
from sparrow_utils.shell import git_revision_info, cmd
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version
from .env import prepare_docker_environment


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


@dataclass
class SparrowConfig:
    bin_directories: typing.List[Path]
    SPARROW_PATH: Path
    bundle_dir: Path
    path_provided: bool
    is_frozen: bool
    version_info: typing.Optional[SparrowVersionMatch] = None

    def __init__(self):
        self.is_frozen = getattr(sys, "frozen", False)
        if self.is_frozen:
            self.bundle_dir = Path(sys._MEIPASS)

        if "SPARROW_PATH" in environ:
            self.path_provided = True
        else:
            # Check if this script is part of a source
            # installation. If so, set SPARROW_PATH to the matching
            # source directory.
            if self.is_frozen:
                pth = self.bundle_dir / "srcroot"
            else:
                this_exe = Path(__file__).resolve()
                pth = this_exe.parent.parent.parent
            self.path_provided = False
            environ["SPARROW_PATH"] = str(pth)

        # Provide environment variable in a more Pythonic way as well
        self.SPARROW_PATH = Path(environ["SPARROW_PATH"])

        self.version_info = test_version(self)

        # Setup path for subcommands
        self._setup_command_path()

        # Set version information needed in compose file
        version = self.find_sparrow_version()
        environ["SPARROW_BACKEND_VERSION"] = version
        environ["SPARROW_FRONTEND_VERSION"] = version
        # Enable native builds and layer caching
        environ["COMPOSE_DOCKER_CLI_BUILD"] = "1"
        environ["DOCKER_BUILDKIT"] = "1"

        prepare_docker_environment()

    def _setup_command_path(self):
        _bin = self.SPARROW_PATH / "_cli" / "bin"
        self.bin_directories = [_bin]
        # Make sure all internal commands can be referenced by name from
        # within Sparrow (even if `sparrow` command itself isn't on the PATH)
        _cmd = environ.get("SPARROW_COMMANDS")
        if _cmd is not None:
            self.bin_directories.append(Path(_cmd))

        # Add location of Sparrow commands to path
        _added_path_dirs = [str(i) for i in self.bin_directories]
        environ["PATH"] = ":".join([*_added_path_dirs, environ["PATH"]])

    def git_revision(self):
        # Setup revision info
        if self.is_frozen:
            rev = (self.bundle_dir / "GIT_REVISION").open().read()
        else:
            rev = git_revision_info(
                capture_output=True, cwd=self.SPARROW_PATH
            ).stdout.decode("utf-8")
        rev = rev.strip()
        return dict(revision=rev, dirty=rev.endswith("-dirty"))

    def find_sparrow_version(self):
        # Get the sparrow version from the command path...
        version = {}
        with (self.SPARROW_PATH / "backend" / "sparrow" / "meta.py").open() as f:
            exec(f.read(), version)
        return version["__version__"]