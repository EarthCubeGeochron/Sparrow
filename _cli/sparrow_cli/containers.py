import sys
import click
from subprocess import Popen, PIPE
from rich import print
from time import sleep

from .env import validate_environment
from .util import compose, container_id, cmd, log
from .help.backend import get_backend_help_info


@click.command()
@click.argument("container", type=str, required=False, default=None)
@click.option("--force-recreate", is_flag=True, default=False)
def sparrow_up(container, force_recreate=False):
    """Bring up the application and start logs"""
    # Validate the presence of SPARROW_SECREY_KEY only if we are bringing
    # the application up. Eventually, this should be wrapped into a Python
    # version of the `sparrow up` command.
    validate_environment()

    if container is None:
        container = ""
    res = compose(
        "up --build --no-start",
        "--force-recreate" if force_recreate else "",
        container,
    )
    if res.returncode != 0:
        print("[red]One or more containers did not build successfully, aborting.[/red]")
        sys.exit(res.returncode)

    # Make sure popen call gets logged...
    _log_cmd = ["sparrow", "logs", container]
    log.debug(" ".join(_log_cmd))
    p = Popen(_log_cmd, stderr=PIPE)

    print("[green]Following container logs[/green]")
    compose("start", container)
    # While we're spinning up, repopulate command help in case it's changed
    get_backend_help_info(cache=True)

    p.wait()


@click.command(name="logs")
@click.argument("container", type=str, required=False, default=None)
def sparrow_logs(container):
    if container is None:
        compose("logs -f --tail=0")
    else:
        id = container_id(container)
        cmd("docker logs -f", id)
