include_server_header = False
workers = 1

# Customize Sparrow's root logger so we don't get overridden by hypercorn
# We may want to customize this further eventually
logconfig_dict = {
    "version": 1,
    "formatters": {
        "colored": {"class": "sparrow.logs.SparrowLogFormatter"},
    },
    "handlers": {
        "error_console": {
            "level": "INFO",
            "formatter": "colored",
            "class": "logging.StreamHandler",
        },
        "default": {
            "level": "DEBUG",
            "formatter": "colored",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["error_console"],
            "level": "INFO",
            "propagate": False,
        },
        "hypercorn.access": {"level": "ERROR", "propagate": False},
        "sparrow": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "__main__": {  # if __name__ == '__main__'
            "handlers": ["error_console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
