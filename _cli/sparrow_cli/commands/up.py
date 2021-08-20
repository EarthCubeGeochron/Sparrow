import sys
import click
from subprocess import Popen
from rich import print
from time import sleep

from ..env import validate_environment
from ..util import compose, cmd, log
from ..help.backend import get_backend_help_info


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
        sleep(1)
        container = ""
    res = cmd(
        "sparrow compose",
        "up --build --no-start",
        "--remove-orphans",
        "--force-recreate" if force_recreate else "",
        container,
    )
    if res.returncode != 0:
        print("[red]One or more containers did not build successfully, aborting.[/red]")
        sys.exit(res.returncode)

    # Make sure popen call gets logged...
    _log_cmd = ["sparrow", "logs", container]
    log.debug(" ".join(_log_cmd))
    p = Popen(_log_cmd)
    sleep(0.05)

    print("[green]Following container logs[/green]")
    compose("start", container)
    # Try to reload nginx server if the container is running
    compose("exec gateway nginx -s reload")
    # While we're spinning up, repopulate command help in case it's changed
    log.info("Caching backend help info")
    get_backend_help_info(cache=True)

    p.wait()
