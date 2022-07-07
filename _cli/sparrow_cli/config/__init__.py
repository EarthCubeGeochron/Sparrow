import typing
from typing import List, Optional
import sys
from dataclasses import dataclass, field
from pathlib import Path
from os import environ
from sparrow_utils.shell import git_revision_info
from sparrow_utils.logs import get_logger, setup_stderr_logs
from pydantic import BaseModel
from enum import Enum

from .environment import prepare_docker_environment, prepare_compose_overrides
from .version_info import SparrowVersionMatch, test_version
from .command_cache import get_backend_command_help, CommandDataSource
from .file_loader import load_config_file
from ..util.exceptions import SparrowCommandError
from ..util.shell import fail_without_docker_command, fail_without_docker_running
from .models import Message, Level

log = get_logger(__file__)

@dataclass
class SparrowConfig:
    bin_directories: typing.List[Path]
    SPARROW_PATH: Path
    path_provided: bool
    is_frozen: bool
    docker_available: bool = False
    bundle_dir: Path = None
    config_file: typing.Optional[Path] = None
    config_dir: typing.Optional[Path] = None
    version_info: typing.Optional[SparrowVersionMatch] = None
    verbose: bool = False
    offline: bool = False
    messages: List[Message] = field(default_factory=list)
    backend_commands: List[dict] = list
    lab_name: Optional[str] = None

    def __init__(self, verbose=False, offline=False):
        self.verbose = verbose
        self.offline = offline
        self.messages = []
        self.is_frozen = getattr(sys, "frozen", False)
        if self.is_frozen:
            self.bundle_dir = Path(sys._MEIPASS)

        self.check_docker_status()

        if verbose:
            setup_stderr_logs("sparrow_cli")
            log.info("Verbose logging enabled")
            # Set verbose environment variable for nested commands
            environ["SPARROW_VERBOSE"] = "1"

        # Load configuration from file!
        self.config_file = load_config_file()
        if self.config_file is None:
            self.messages.append(
                Message(
                    id="no-config-file",
                    text="No lab configuration file found",
                    details="Create a [cyan]sparrow-config.sh[/cyan] file in a project directory to set up a lab.",
                )
            )
        else:
            self.config_dir = self.config_file.parent

        if "SPARROW_PATH" in environ:
            self.path_provided = True
            source_root = Path(environ["SPARROW_PATH"])

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

        res = get_backend_command_help()
        self.backend_commands = res.data
        if res.source == CommandDataSource.default:
            self.messages.append(
                Message(
                    id="backend-commands",
                    text="Plugin commands have not yet been loaded from Sparrow core",
                    details="Run [cyan]sparrow up[/cyan] to populate the configuration cache.",
                )
            )

        self.lab_name = environ.get("SPARROW_LAB_NAME")

        # Provide environment variable in a more Pythonic way as well
        source_root = Path(environ["SPARROW_PATH"])
        self.SPARROW_PATH = source_root
        _is_correct_source = (
            source_root.is_dir() and (source_root / "sparrow-version.json").is_file()
        )
        if not _is_correct_source:
            raise SparrowCommandError(
                "The SPARROW_PATH environment variable does not appear to point to a Sparrow source directory.",
                details=f"SPARROW_PATH={environ['SPARROW_PATH']}",
            )

        self.version_info = test_version(self)
        self.add_revision_message()

        # Setup path for subcommands
        self._setup_command_path()

        # Set version information needed in compose file
        # Packages use canonicalized version string, no matter how it is represented in tags
        version = self.find_sparrow_version()
        # Pin the images used in the compose file to the current version, unless
        # otherwise specified.
        tag = f":{version}"
        if self.offline:
            environ["SPARROW_OFFLINE"] = "1"
            log.info("Running in offline mode by using any available image")
            tag = ""

        image_prefix = "ghcr.io/earthcubegeochron/sparrow"

        environ.setdefault("SPARROW_BACKEND_IMAGE", f"{image_prefix}/backend" + tag)
        environ.setdefault("SPARROW_FRONTEND_IMAGE", f"{image_prefix}/frontend" + tag)

        prepare_docker_environment()
        if "COMPOSE_FILE" in environ:
            self.messages.append(
                Message(
                    id="custom-compose",
                    text="COMPOSE_FILE provided, skipping overrides and profiles.",
                    details="Only do this if you know what you're doing!",
                    level=Level.WARNING
                )
            )
        else:
            self.messages += prepare_compose_overrides()

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

    def add_revision_message(self):
        ver = self.version_info
        if not ver:
            return
        rev = "revision" if ver.uses_git else "version"
        msg = "matches" if ver.is_match else "does not match"
        msg = f"Sparrow {rev} [underline]{ver.available}[/underline] {msg} [underline]{ver.desired}[/underline]"
        self.messages.append(Message(id="version-match", text=msg, level=Level.SUCCESS))

    def find_sparrow_version(self):
        # Get the sparrow version from the command path...
        version = {}
        with (self.SPARROW_PATH / "backend" / "sparrow" / "meta.py").open() as f:
            exec(f.read(), version)
        return version["__version__"]

    def is_source_install(self):
        return not self.is_frozen or self.path_provided

    def check_docker_status(self):
        try:
            fail_without_docker_command()
        except SparrowCommandError as err:
            self.messages.append(
                Message(
                    id="docker-not-installed",
                    text="Docker is not installed",
                    details=str(err),
                    level=Level.ERROR,
                )
            )
        try:
            fail_without_docker_running()
        except SparrowCommandError as err:
            self.messages.append(
                Message(
                    id="docker-not-running",
                    text="Docker is not running",
                    details=str(err),
                    level=Level.ERROR,
                )
            )
        self.docker_available = True
