from .test import sparrow_test
from .test_lab import sparrow_test_lab
from .database import sparrow_db
from .docs import sparrow_docs
from .dev import sparrow_dev
from .info import sparrow_info
from .build import sparrow_build
from .attach import sparrow_attach
from .tasks import tasks
from .logs import sparrow_logs
from .up import sparrow_up
from .docker import sparrow_docker_prune

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
    "prune": sparrow_docker_prune,
    "tasks": tasks,
}


def add_commands(cli):
    for name, command in _commands.items():
        cli.add_command(command, name=name)
