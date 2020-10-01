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
