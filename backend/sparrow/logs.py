import logging


def console_handler():
    console = logging.StreamHandler()
    # create console handler and set level to debug
    console.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # add formatter to ch
    console.setFormatter(formatter)


def get_logger(name, level=logging.DEBUG, handler=None):
    log = logging.getLogger(name)
    log.setLevel(level)
    # add ch to logger
    if handler:
        log.addHandler(handler)
    return log
