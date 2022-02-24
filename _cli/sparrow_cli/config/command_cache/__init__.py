import json
from json.decoder import JSONDecodeError
import os
from pathlib import Path
from hashlib import md5
from subprocess import PIPE
from pydantic import BaseModel
from enum import Enum

from ...util.shell import exec_or_run
from ...util.exceptions import SparrowCommandError
from sparrow_utils import relative_path


def dirhash(path):
    abspath = Path(path).absolute()
    hash_object = md5(str(abspath).encode())
    return hash_object.hexdigest()[:8]


def cache_dir(create=False):
    """Unixy cache directory for application files"""
    __dir = Path.home() / ".cache" / "org.earthcube.sparrow"
    if create:
        __dir.mkdir(parents=True, exist_ok=True)
    return __dir


def cli_cache_file():
    cfg = os.environ.get("SPARROW_CONFIG_DIR", None)
    prefix = "sparrow"
    if cfg is not None:
        prefix = dirhash(cfg)
    return cache_dir(create=True) / f"{prefix}-cli-options.json"


def get_backend_help_info(write_cache=True):
    env = dict(**os.environ)
    env["SPARROW_SECRET_KEY"] = env.get("SPARROW_SECRET_KEY", "Test")
    out = exec_or_run(
        "backend",
        "/app/sparrow/__main__.py",
        "get-cli-info",
        stdout=PIPE,
        env=env,
        tty=False,
        run_args=("--no-deps --rm",),
    )
    if out.returncode != 0:
        details = str(b"\n".join(out.stdout.splitlines()[1:]), "utf-8") + "\n"
        raise SparrowCommandError(
            "Could not access help text for sparrow backend", details=details
        )

    data = out.stdout.decode("utf-8").strip()
    try:
        _decoded = json.loads(data)
        if write_cache:
            cachefile = cli_cache_file()
            cachefile.open("w").write(data)
        return _decoded
    except JSONDecodeError as err:
        raise SparrowCommandError(
            "Could not decode JSON response from backend", details=data
        )


class CommandDataSource(str, Enum):
    default = "default"
    cached = "cached"
    direct = "direct"


class ContainerCommandData(BaseModel):
    data: dict
    source: CommandDataSource


def get_backend_command_help():
    cache_file = cli_cache_file()
    try:
        if cache_file.is_file():
            return ContainerCommandData(
                data=json.load(cache_file.open("r")), source=CommandDataSource.cached
            )
    except Exception as err:
        raise SparrowCommandError(
            f"Could not read cache file {cache_file}", details=str(err)
        )
    return ContainerCommandData(
        data=json.load(open(relative_path(__file__, "default-backend-commands.json"))),
        source=CommandDataSource.default,
    )
