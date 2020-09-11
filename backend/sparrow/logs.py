import logging
from colorlog import StreamHandler, ColoredFormatter

# disabled 'levelname'
formatter = ColoredFormatter(
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

console_handler = StreamHandler()
# create console handler and set level to debug
# console_handler.setLevel(logging.CRITICAL)
# create formatter
# add formatter to ch
console_handler.setFormatter(formatter)


def get_logger(name=None, level=logging.DEBUG, handler=None):
    log = logging.getLogger(name)
    log.setLevel(level)
    if handler:
        log.addHandler(handler)
    return log


# Customize Sparrow's root logger so we don't get overridden by uvicorn
# We may want to customize this further eventually
# https://github.com/encode/uvicorn/issues/410
# logger = logging.getLogger("sparrow")
# if logger.hasHandlers():
#    logger.handlers.clear()
# logger.addHandler(console_handler)
