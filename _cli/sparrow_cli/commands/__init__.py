from .test import sparrow_test  # noqa
from .test_lab import sparrow_test_lab
from .database import sparrow_db  # noqa
from .docs import sparrow_docs  # noqa
from .dev import sparrow_dev  # noqa
from .info import sparrow_info  # noqa
from .build import sparrow_build


def add_commands(cli):
    cli.add_command(sparrow_build, name="build")
    cli.add_command(sparrow_dev, name="dev")
    cli.add_command(sparrow_info, name="info")
    cli.add_command(sparrow_docs, name="docs")
    cli.add_command(sparrow_db, name="db")
    cli.add_command(sparrow_test, name="test")
    cli.add_command(sparrow_test_lab, name="create-test-lab")