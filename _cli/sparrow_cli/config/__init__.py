import typing
import sys
from dataclasses import dataclass
from pathlib import Path
from os import environ, chdir
from sparrow_utils.shell import git_revision_info, cmd
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version
from .environment import prepare_docker_environment
from .version_info import SparrowVersionMatch, test_version


@dataclass
class SparrowConfig:
    bin_directories: typing.List[Path]
    SPARROW_PATH: Path
    bundle_dir: Path
    path_provided: bool
    is_frozen: bool
    config_dir: typing.Optional[Path] = None
    version_info: typing.Optional[SparrowVersionMatch] = None
    verbose: bool = False

    def __init__(self, verbose=False):
        self.verbose = verbose
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
                pth = this_exe.parent.parent.parent.parent
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
        # https://docs.docker.com/develop/develop-images/build_enhancements/
        # This is kind of experimental
        environ.setdefault("COMPOSE_DOCKER_CLI_BUILD", "1")
        environ.setdefault("DOCKER_BUILDKIT", "1")

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
