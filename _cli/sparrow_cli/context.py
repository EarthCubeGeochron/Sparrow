import typing
import sys
from dataclasses import dataclass
from pathlib import Path
from os import environ
from .env import setup_command_path


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

        # Check if this script is part of a source
        # installation. If so, set SPARROW_PATH accordingly
        if "SPARROW_PATH" not in environ:
            if self.is_frozen:
                pth = self.bundle_dir / "srcroot"
            else:
                this_exe = Path(__file__).resolve()
                pth = this_exe.parent.parent.parent
            self.path_provided = False
            environ["SPARROW_PATH"] = str(pth)
        # Provide environment variable in a more Pythonic way as well
        self.SPARROW_PATH = Path(environ["SPARROW_PATH"])

        # Setup path for subcommands
        self.bin_directories = setup_command_path()
