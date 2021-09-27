import typing
import sys
from dataclasses import dataclass
from pathlib import Path
from os import environ, getenv
from sparrow_utils.shell import git_revision_info
from sparrow_utils.logs import get_logger, setup_stderr_logs

from .environment import prepare_docker_environment, prepare_compose_overrides
from .version_info import SparrowVersionMatch, test_version
from .file_loader import load_config_file

log = get_logger(__file__)


@dataclass
class SparrowConfig:
    bin_directories: typing.List[Path]
    SPARROW_PATH: Path
    bundle_dir: Path
    path_provided: bool
    is_frozen: bool
    config_file: typing.Optional[Path] = None
    config_dir: typing.Optional[Path] = None
    version_info: typing.Optional[SparrowVersionMatch] = None
    verbose: bool = False
    offline: bool = False

    def __init__(self, verbose=False, offline=False):
        self.verbose = verbose
        self.offline = offline
        self.is_frozen = getattr(sys, "frozen", False)
        if self.is_frozen:
            self.bundle_dir = Path(sys._MEIPASS)

        if verbose:
            setup_stderr_logs("sparrow_cli")
            log.info("Verbose logging enabled")
            # Set verbose environment variable for nested commands
            environ["SPARROW_VERBOSE"] = "1"

        # Load configuration from file!
        self.config_file = load_config_file()
        if self.config_file is not None:
            self.config_dir = self.config_file.parent

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
        # Pin the images used in the compose file to the current version, unless
        # otherwise specified.
        tag = f":{version}"
        if self.offline:
            environ["SPARROW_OFFLINE"] = "1"
            log.info("Running in offline mode by using any available image")
            tag = ""

        environ.setdefault("SPARROW_BACKEND_IMAGE", "sparrow/backend" + tag)
        environ.setdefault("SPARROW_FRONTEND_IMAGE", "sparrow/frontend" + tag)

        # will set COMPOSE_PROJECT_NAME if undefined
        self.set_compose_lab_name()

        prepare_docker_environment()
        if "COMPOSE_FILE" in environ:
            log.info("COMPOSE_FILE provided; skipping overrides and profiles.")
        else:
            prepare_compose_overrides()

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

    def set_compose_lab_name(self):
        """method to cascade environ variables to get a lab instance name"""

        compose_name = getenv("COMPOSE_PROJECT_NAME", None)
        lab_name = getenv("SPARROW_LAB_NAME", None)
        config_dir = getenv("SPARROW_CONFIG_DIR", None)

        if compose_name is None:
            if lab_name is not None:
                lab_name = "_".join(lab_name.split()).lower()  # format
                environ.setdefault("COMPOSE_PROJECT_NAME", lab_name)
            elif config_dir is not None:
                lab_name = config_dir.split("/")[-1].lower()
                environ.setdefault("COMPOSE_PROJECT_NAME", lab_name)
                environ.setdefault("SPARROW_LAB_NAME", lab_name)
            else:
                lab_name = 'sparrow'
                environ.setdefault("COMPOSE_PROJECT_NAME", lab_name)
                environ.setdefault("SPARROW_LAB_NAME", lab_name)
