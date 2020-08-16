import logging
from colorlog import StreamHandler, ColoredFormatter
from uvicorn.logging import DefaultFormatter

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


def console_handler():
    console = StreamHandler()
    # create console handler and set level to debug
    console.setLevel(logging.DEBUG)
    # create formatter
    # add formatter to ch
    console.setFormatter(formatter)
    return console


def get_logger(name, level=logging.DEBUG, handler=None):
    log = logging.getLogger(name)
    log.setLevel(level)
    # add ch to logger
    if handler:
        log.addHandler(handler)
    else:
        # This is likely to be slow
        log.addHandler(console_handler())
    return log
