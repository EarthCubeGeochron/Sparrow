import typing
from typing import List, Optional
import sys
from dataclasses import dataclass, field
from pathlib import Path
from os import environ
from macrostrat.utils.shell import git_revision_info
from macrostrat.utils.logs import get_logger, setup_stderr_logs
from pydantic import BaseModel
from enum import Enum

from .environment import (
    is_truthy,
    prepare_docker_environment,
    prepare_compose_overrides,
)
from .version_info import SparrowVersionMatch, test_version
from .command_cache import get_backend_command_help, CommandDataSource
from .file_loader import load_config_file
from ..util.exceptions import SparrowCommandError
from ..util.shell import (
    fail_without_docker_command,
    has_command,
    fail_without_docker_running,
)
from .models import Message, Level
from ..upgrade_database import check_database_cluster_version, version_images

log = get_logger(__file__)


@dataclass
class SparrowConfig:
    bin_directories: typing.List[Path]
    SPARROW_PATH: Path
    project_name: str
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

    # The PostgreSQL major version required for this Sparrow instance
    postgres_supported_version: int = 14
    postgres_current_version: int = None

    # Whether we will try to run the frontend locally
    local_frontend: bool = False

    def __init__(self, verbose=False, offline=False):
        self.verbose = verbose
        self.offline = offline
        self.messages = []

        # Important: define if we're running under pyinstaller.
        self.is_frozen = getattr(sys, "frozen", False)
        if self.is_frozen:
            self.bundle_dir = Path(sys._MEIPASS)

        self.check_docker_status()

        if verbose:
            setup_stderr_logs("sparrow_cli")
            setup_stderr_logs("docker")
            log.info("Verbose logging enabled")
            # Set verbose environment variable for nested commands
            environ["SPARROW_VERBOSE"] = "1"

        # Load configuration from file!
        self.config_file = load_config_file()
        if self.config_file is None:
            self.add_message(
                id="no-config-file",
                text="No lab configuration file found",
                details="Create a [cyan]sparrow-config.sh[/cyan] file in a project directory to set up a lab.",
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
            self.add_message(
                id="backend-commands",
                text="Plugin commands have not yet been loaded from Sparrow core",
                details="Run [cyan]sparrow up[/cyan] to populate the configuration cache.",
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

        self.project_name = self.infer_project_name()
        self.local_frontend = self.configure_local_frontend()

        # Check database version
        self.check_database_version()

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
            self.add_message(
                id="custom-compose",
                text="COMPOSE_FILE provided, skipping overrides and profiles.",
                details="Only do this if you know what you're doing!",
                level=Level.WARNING,
            )
        else:
            self.messages += prepare_compose_overrides(self)

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
        level = Level.SUCCESS if ver.is_match else Level.ERROR
        self.add_message(id="version-match", text=msg, level=level)

    def find_sparrow_version(self):
        # Get the sparrow version from the command path...
        version = {}
        with (
            self.SPARROW_PATH / "backend" / "sparrow" / "core" / "meta.py"
        ).open() as f:
            exec(f.read(), version)
        return version["__version__"]

    def add_message(self, **kwargs: Message):
        self.messages.append(Message(**kwargs))

    def infer_project_name(self):
        """
        In CLI version 4, we try to impose some rigor on the COMPOSE_PROJECT_NAME
        variable, so that we can create reliable mappings between docker-compose
        service and volume names.
        """
        project_name = environ.get("COMPOSE_PROJECT_NAME")
        if project_name is not None:
            return project_name
        # We could eventually start referring to projects by the SPARROW_LAB_NAME
        # environment variable, but for now we'll just use the current directory name
        # (the default for docker-compose)
        project_name = (
            self.SPARROW_PATH.stem.replace("-", "_").replace(" ", "_").lower()
        )

        self.add_message(
            id="project-name",
            text=f"Project name [underline]{project_name}[/underline] inferred",
            details="COMPOSE_PROJECT_NAME not set, inferring from Sparrow root directory name.",
            level=Level.WARNING,
        )
        return project_name

    def is_source_install(self):
        return not self.is_frozen or self.path_provided

    def check_docker_status(self):
        try:
            fail_without_docker_command()
        except SparrowCommandError as err:
            self.add_message(
                id="docker-not-installed",
                text="Docker is not installed",
                details=str(err),
                level=Level.ERROR,
            )
        try:
            fail_without_docker_running()
        except SparrowCommandError as err:
            self.add_message(
                id="docker-not-running",
                text="Docker is not running",
                details=str(err),
                level=Level.ERROR,
            )
        self.docker_available = True

    def configure_local_frontend(self):
        # If we are running a local frontend
        _local_frontend = is_truthy("SPARROW_LOCAL_FRONTEND")
        # Check for yarn
        if not _local_frontend:
            return False
        if not has_command("node"):
            self.add_message(
                "Cannot run frontend locally without [bold]node[/bold] available.",
                level=Level.ERROR,
            )
            _local_frontend = False
        if self.is_frozen:
            self.add_message(
                "Cannot run frontend locally in a frozen environment.",
                level=Level.ERROR,
            )
            _local_frontend = False
        return _local_frontend

    def check_database_version(self):
        cluster_volume_name = self.project_name.lower() + "_db_cluster"
        version = check_database_cluster_version(cluster_volume_name)
        self.postgres_current_version = version
        if version is None:
            self.add_message(
                id="no-database-cluster",
                text="No database cluster",
                details=[
                    "The database cluster has not yet been initialized.",
                    "Run [bold]sparrow up[/bold] or [bold]sparrow init[/bold] to create one.",
                ],
                level=Level.WARNING,
            )
            return

        upgrade_text = " No upgrade path is available — perhaps you have downgraded your Sparrow installation?"
        if (
            version < self.postgres_supported_version
            and version_images[version] is not None
        ):
            upgrade_text = (
                " Run [cyan]sparrow db update[/cyan] to upgrade the database."
            )
        if version < self.postgres_supported_version:
            self.add_message(
                id="postgresql-version",
                text=f"PostgreSQL version {self.postgres_supported_version} is required",
                details=f"Sparrow's database cluster is running PostgreSQL version {version}."
                + upgrade_text,
                level=Level.ERROR,
            )
            # Fall back to old database version
            environ["SPARROW_DATABASE_IMAGE"] = version_images[version]
        else:
            self.add_message(
                id="postgresql-version",
                text=f"Using PostgreSQL version {version}",
                level=Level.SUCCESS,
            )
