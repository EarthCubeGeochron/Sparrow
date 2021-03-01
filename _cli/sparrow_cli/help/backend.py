import json
from json.decoder import JSONDecodeError
import os
from pathlib import Path
from hashlib import md5
from ..util import compose, exec_sparrow
from ..exc import SparrowCommandError
from subprocess import PIPE


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


def get_backend_help_info(cache=True):
    env = dict(**os.environ)
    env["SPARROW_SECRET_KEY"] = env.get("SPARROW_SECRET_KEY", "Test")
    out = compose(
        "run --no-deps --rm -T",
        "backend",
        "/app/sparrow/__main__.py",
        "get-cli-info",
        stdout=PIPE,
        env=env,
    )
    if out.returncode != 0:
        details = str(b"\n".join(out.stdout.splitlines()[1:]), "utf-8") + "\n"
        raise SparrowCommandError(
            "Could not access help text for sparrow backend", details=details
        )

    data = out.stdout.decode("utf-8").strip()
    try:
        _decoded = json.loads(data)
        if cache:
            cachefile = cli_cache_file()
            cachefile.open("w").write(data)
        return _decoded
    except JSONDecodeError as err:
        raise SparrowCommandError(
            "Could not decode JSON response from backend", details=data
        )


def get_backend_command_help():
    cachefile = cli_cache_file()
    try:
        if cachefile.is_file():
            return json.load(cachefile.open("r"))
    except Exception:
        pass
    return get_backend_help_info(cache=True)
