from shlex import split
from subprocess import run

from .logs import get_logger

log = get_logger(__name__)


def cmd(*v, **kwargs):
    logger = kwargs.pop("logger", log)
    val = " ".join(v)
    logger.debug(val)
    return run(split(val), **kwargs)