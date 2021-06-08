from shlex import split
from subprocess import run

from .logs import get_logger

log = get_logger(__name__)


def split_args(*args):
    return split(" ".join(args))


def cmd(*v, **kwargs):
    logger = kwargs.pop("logger", log)
    val = " ".join(v)
    logger.debug(val)
    return run(split(val), **kwargs)


def git_revision_info(**kwargs):
    """Get a descriptor of the current git revision (usually used for bundling purposes).
    This will be in the format <short-commit-hash>[-dirty]?, e.g. `ee26194-dirty`.
    """
    return cmd("git describe --match=NOT-EVER-A-TAG --always --abbrev --dirty", **kwargs)
