import typing
import sys
from dataclasses import dataclass
from pathlib import Path
from os import environ
from .env import setup_command_path
from .exc import SparrowCommandError
from sparrow_utils.shell import git_revision_info, cmd
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version


def get_commit(cfg, match="HEAD"):
    rev = cmd(
        "git rev-parse --short",
        match + "^{commit}",
        cwd=cfg.SPARROW_PATH,
        capture_output=True,
    )
    return rev.stdout.decode("utf-8").strip()


def test_version(cfg):
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
        actual_version = Version(cfg.find_sparrow_version())
        if actual_version in spec:
            return
        else:
            raise SparrowCommandError(
                f"Sparrow version {actual_version} is not in {spec}"
            )
    except InvalidSpecifier:
        pass

    # Fall back to git-based version string parsing...
    if cfg.is_frozen and not cfg.path_provided:
        rev = cfg.git_revision()["revision"].removesuffix("-dirty")
    else:
        rev = get_commit(cfg, "HEAD")

    match_rev = get_commit(cfg, required_version)
    try:
        assert rev == match_rev
        # print(f"Git revision {rev} matches specifier {required_version}")
    except AssertionError:
        raise SparrowCommandError(
            f"Sparrow version {rev} does not match {required_version} (with hash {match_rev})"
        )


@dataclass
class SparrowConfig:
    bin_directories: typing.List[Path]
    SPARROW_PATH: Path
    bundle_dir: Path
    path_provided: bool
    is_frozen: bool

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

        test_version(self)

        # Setup path for subcommands
        self.bin_directories = setup_command_path()

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