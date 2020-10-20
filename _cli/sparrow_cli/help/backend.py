import re
import json
import os
from click import secho, echo
from pathlib import Path
from rich.console import Console
from subprocess import PIPE, STDOUT
from ..util import cmd, exec_or_run
from hashlib import md5
from ..exc import SparrowCommandError


def dirhash(path):
    abspath = Path(path).absolute()
    hash_object = md5(str(abspath).encode())
    return hash_object.hexdigest()[:8]


def cache_dir(create=False):
    """Unixy cache directory for application files"""
    __dir = Path.home() / ".cache" / "sparrow"
    if create:
        __dir.mkdir(parents=True, exist_ok=True)
    return __dir


def cli_cache_file():
    cfg = os.environ.get("SPARROW_CONFIG_DIR", None)
    prefix = "sparrow"
    if cfg is not None:
        prefix = dirhash(cfg)
    return cache_dir(create=True) / f"{prefix}-cli-hash.json"


def get_backend_command_help():
    cachefile = cli_cache_file()
    if cachefile.is_file():
        with cachefile.open("r") as f:
            return json.load(f)
    out = exec_or_run(
        "backend", "cat /run/cli-info.json", tty=False, stdout=PIPE, stderr=STDOUT
    )
    if out.returncode != 0:
        raise SparrowCommandError("Could not access help text for sparrow backend")
    with cachefile.open("w") as f:
        f.write_line("sdwrqewrfedif")
    return json.loads(str(out.stdout, "utf-8"))
