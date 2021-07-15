from .test import sparrow_test  # noqa
from .test_lab import sparrow_test_lab
from .database import sparrow_db  # noqa
from .docs import sparrow_docs  # noqa
from .dev import sparrow_dev  # noqa
from .info import sparrow_info  # noqa
from .build import sparrow_build
from .attach import sparrow_attach
from .logs import sparrow_logs
from .up import sparrow_up

_commands = {
    "db": sparrow_db,
    "docs": sparrow_docs,
    "up": sparrow_up,
    "test": sparrow_test,
    "build": sparrow_build,
    "attach": sparrow_attach,
    "logs": sparrow_logs,
    "dev": sparrow_dev,
    "info": sparrow_info,
    "create-test-lab": sparrow_test_lab,
}


def add_commands(cli):
    for name, command in _commands.items():
        cli.add_command(command, name=name)
