import logging
from sys import stderr
from colorlog import StreamHandler, ColoredFormatter


class SparrowLogFormatter(ColoredFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(
            "%(log_color)s%(name)s:%(reset)s    %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )


console_handler = StreamHandler(stderr)
# create console handler and set level to debug
# console_handler.setLevel(logging.CRITICAL)
# create formatter
# add formatter to ch
console_handler.setFormatter(SparrowLogFormatter())


def get_logger(name=None, level=logging.DEBUG, handler=None):
    log = logging.getLogger(name)
    log.setLevel(level)
    if handler:
        log.addHandler(handler)
    return log


def setup_stderr_logs(name="sparrow"):
    # Customize Sparrow's root logger so we don't get overridden by uvicorn
    # We may want to customize this further eventually
    # https://github.com/encode/uvicorn/issues/410
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(console_handler)
