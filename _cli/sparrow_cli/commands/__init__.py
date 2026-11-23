from .attach import sparrow_attach
from .build import sparrow_build
from .database import sparrow_db
from .dev import sparrow_dev
from .docs import sparrow_docs
from .info import sparrow_info
from .logs import sparrow_logs
from .tasks import tasks
from .test import sparrow_test
from .test_lab import sparrow_test_lab
from .up import sparrow_restart, sparrow_up
from .update import sparrow_update, sparrow_upgrade

_commands = {
    "db": sparrow_db,
    "docs": sparrow_docs,
    "up": sparrow_up,
    "restart": sparrow_restart,
    "update": sparrow_update,
    "upgrade": sparrow_upgrade,
    "test": sparrow_test,
    "build": sparrow_build,
    "attach": sparrow_attach,
    "logs": sparrow_logs,
    "dev": sparrow_dev,
    "info": sparrow_info,
    "create-test-lab": sparrow_test_lab,
    "tasks": tasks,
}


def add_commands(cli):
    for name, command in _commands.items():
        cli.add_command(command, name=name)
