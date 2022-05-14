from shlex import split
from subprocess import run as _run

from .logs import get_logger

log = get_logger(__name__)


def split_args(*args):
    return split(" ".join(args))

def run(*args, **kwargs):
    logger = kwargs.pop("logger", log)
    logger.debug(args)
    return _run(args, **kwargs)

def cmd(*args, **kwargs):
    if kwargs.pop("collect_args", True):
        args = split_args(*args)
    return run(*args, **kwargs)


def git_revision_info(**kwargs):
    """Get a descriptor of the current git revision (usually used for bundling purposes).
    This will be in the format <short-commit-hash>[-dirty]?, e.g. `ee26194-dirty`.
    """
    return cmd(
        "git describe --match=NOT-EVER-A-TAG --always --abbrev --dirty", **kwargs
    )
