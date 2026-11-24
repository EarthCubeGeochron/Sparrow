from os import environ
from pathlib import Path
from typing import Optional


def get_data_directory() -> Optional[Path]:
    """The lab's data directory, for labs that keep files on a disk."""
    value = environ.get("SPARROW_DATA_DIR")
    if value is None:
        return None
    return Path(value)
