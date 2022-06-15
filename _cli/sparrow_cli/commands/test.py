import click
import sys
from os import environ, chdir
from rich import print
from textwrap import dedent

from sparrow_cli.util.command_groups import SparrowDefaultCommand
from ..util import cmd, exec_or_run
from sparrow_utils import get_logger

log = get_logger(__name__)


class TestGroup(SparrowDefaultCommand):
    """
    Usage: sparrow test \[subcommand?] OPTIONS... PYTEST_OPTIONS...

    [bold]Backend tests[/bold] (default)

    Options:
    --help                      Print this page and exit
    --psql                      Provide a psql prompt when testing concludes
    --teardown / --no-teardown  Shut down docker containers on exit
    --quick                     Keep databases and Docker containers

    All command line options specified at the end of the command are passed
    to the [bold]pytest[/bold] test runner.

    --pytest-help               Show help for the pytest runner

    Custom additions to PYTEST_OPTIONS:

    --include-slow              Include slow-running tests
    --no-isolate                Disable transaction isolation between test
                                classes


    Motivating examples:

    > Stop on first test and don't capture stdout:
        [cyan]sparrow test --capture=no --maxfail=0[/cyan]
    > Repeat a single test:
        [cyan]sparrow test -k test_incomplete_import_excluded[/cyan]
    > Only PyChron tests:
        [cyan]sparrow test --quick -k pychron[/cyan]
    > Run previously failed tests first, and stop on failure:
        [cyan]sparrow test --ff -x[/cyan]

    [bold]Other subcommands[/bold]:

    cli                         Run tests of the Sparrow CLI
    dump-dz-database            Dump an instance of a Sparrow database
                                with testing data, to test migrations
    """

    ignore_unknown_options = True

    @classmethod
    def echo_help(cls, ctx):
        print(dedent(cls.__doc__))
        ctx.exit()

    def parse_args(self, ctx, args):
        """Override to make sure we get subcommand help on base `sparrow help` invocation.
        Solution found at https://github.com/click-contrib/click-default-group/issues/14
        """
        if args in (["-h"], ["--help"]) and self.default_if_no_args:
            return TestGroup.echo_help(ctx)
        if not args:
            args.insert(0, self.default_cmd_name)
        return super(SparrowDefaultCommand, self).parse_args(ctx, args)


def compose(*args, **kwargs):
    env = dict(**environ)
    env.update(
        # Set a different compose project name so we don't step on running
        # applications.
        COMPOSE_PROJECT_NAME="sparrow_test",
        COMPOSE_FILE="docker-compose.testing.yaml",
    )
    kwargs["env"] = env
    return cmd("sparrow compose", *args, **kwargs)


__ctx = dict(ignore_unknown_options=True, help_option_names=[])


@click.group(name="test", cls=TestGroup, default="app", default_if_no_args=True)
@click.pass_context
def sparrow_test(ctx):
    """Test runner for the Sparrow application. The testing framework is based on
    PyTest."""
    pth = environ.get("SPARROW_PATH", None)
    if pth is None:
        print(
            "SPARROW_PATH not found. For now, tests can only be run when "
            "a source directory is available."
        )
        ctx.exit()
    chdir(pth)

# Ideally this would be a subcommand, not its own separate command
@sparrow_test.command("cli", context_settings=__ctx)
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cli_tests(ctx, pytest_args):
    # First, test basic operation of command-line application
    # We should probably just import pytest directly and run
    pass_conditions = {0: "Tests passed", 5: "No tests collected"}

    res = cmd("_cli/_scripts/test-cli", *pytest_args)
    if res.returncode not in pass_conditions.keys():
        print("CLI tests failed, exiting")
        sys.exit(res.returncode)
    else:
        print(f"CLI: {pass_conditions[res.returncode]}")


# Ideally this would be a subcommand, not its own separate command
@sparrow_test.command("app", context_settings=__ctx)
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.option("--help", is_flag=True, default=False, help="Print this page and exit")
@click.option(
    "--pytest-help", is_flag=True, default=False, help="Print the PyTest help"
)
@click.option(
    "--psql",
    is_flag=True,
    default=False,
    help="Provide a psql prompt when testing concludes",
)
@click.option(
    "--teardown/--no-teardown",
    is_flag=True,
    default=True,
    help="Shut down docker containers on exit",
)
@click.option(
    "--quick", is_flag=True, default=False, help="Keep databases and Docker containers"
)
@click.pass_context
def sparrow_test_main(
    ctx,
    pytest_args,
    help=False,
    pytest_help=False,
    psql=False,
    teardown=True,
    quick=False,
):
    """Run the Sparrow's main application tests"""
    if help:
        # We override the help method so we can add extra information.
        TestGroup.echo_help(ctx)

    if pytest_help:
        cmd("pytest --help")
        ctx.exit()

    pth = environ.get("SPARROW_PATH", None)
    if pth is None:
        print(
            "SPARROW_PATH not found. For now, tests can "
            "only be run when a source directory is available."
        )
        return

    print("Preparing [cyan]Sparrow[/cyan] application images")

    res = compose("build")
    if res.returncode != 0:
        print("[red]ERROR[/red]: Could not run tests")
        sys.exit(res.returncode)

    print("Running sparrow tests")

    # Need to bring up database separately to ensure ports are mapped...
    # if not container_is_running("db"):
    # compose("up -d db")
    # if container_is_running("backend") and not standalone:
    #     res = compose("exec backend", "/bin/run-tests", *args, flag)
    # else:

    res = compose("run --rm --service-ports backend", "pytest", "/app", *pytest_args)
    # if "--keep-database" not in args:
    if psql:
        print(
            "Initializing psql shell. "
            "The database is also available on localhost port 54322"
        )
        compose(
            "run --rm --service-ports backend psql -h db -p 5432 -U postgres sparrow_test"
        )

    if quick:
        teardown = False
    if teardown:
        compose("down --remove-orphans")
    log.debug(f"Exiting with return code {res.returncode}")
    sys.exit(res.returncode)


def indb(*args, **kwargs):
    return compose("exec db", *args, **kwargs)


@sparrow_test.command("dump-dz-database")
def dump_database():
    """Dump a basic test database containing one detrital zircon sample to stdout"""
    exec_or_run("backend", "sparrow_tests/scripts/dump-test-database.py", tty=False)


sparrow_test.add_shell_command("integration", "Run integration tests", prefix="sparrow-test-")
