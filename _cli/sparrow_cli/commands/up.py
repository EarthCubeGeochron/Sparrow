import sys
import click
from subprocess import Popen
from rich import print
from time import sleep

from ..config.environment import validate_environment
from ..config import SparrowConfig
from ..util import compose, cmd, log
from ..help import get_backend_help_info


@click.command()
@click.argument("container", type=str, required=False, default="")
@click.option("--force-recreate", is_flag=True, default=False)
@click.pass_context
def sparrow_up(ctx, container="", force_recreate=False):
    """Bring up the application and start logs"""
    # Validate the presence of SPARROW_SECREY_KEY only if we are bringing
    # the application up. Eventually, this should be wrapped into a Python
    # version of the `sparrow up` command.
    validate_environment()

    cfg = ctx.find_object(SparrowConfig)

    # build containers
    if not cfg.offline:
        cmd("sparrow compose build")

    # Run the prebuild script
    prebuild = cfg.config_dir / "sparrow-prestart.sh"
    if prebuild.exists():
        log.debug("Running prebuild script")
        cmd("bash", str(prebuild))

    # Bring up the application
    res = cmd(
        "sparrow compose",
        "up --no-build --no-start",
        "--remove-orphans",
        "--force-recreate" if force_recreate else "",
        container,
    )
    if res.returncode != 0:
        print("[red bold]One or more containers did not build successfully, aborting.")
        sys.exit(res.returncode)
    else:
        print("[green bold]All containers built successfully.")
    print()

    print("[green bold]Starting the Sparrow application!")

    # Check if containers are running
    res = compose("ps --services --filter status=running", capture_output=True)
    running_containers = res.stdout.decode("utf-8").strip()
    if running_containers != "" and not force_recreate:
        print("[dim]Some containers are already running and up to date: ")
        print("  " + ", ".join(running_containers.split("\n")))
        print(
            "[dim]To fully restart Sparrow, run [cyan]sparrow restart[/cyan] or [cyan]sparrow up --force-recreate[/cyan]."
        )
    print()

    print("[green bold]Following container logs")
    print("[dim]- Press Ctrl+c to exit (Sparrow will keep running).")
    print("[dim]- Sparrow can be stopped with the [cyan]sparrow down[/cyan] command.")
    print()

    # Make sure popen call gets logged...
    _log_cmd = ["sparrow", "logs", container]
    log.debug(" ".join(_log_cmd))
    p = Popen(_log_cmd)
    # Wait a tick to make sure the logs are started
    sleep(0.05)

    compose("start", container)

    # Try to reload nginx server if the container is running
    if "gateway" in running_containers:
        compose("exec gateway nginx -s reload")

    # While we're spinning up, repopulate command help in case it's changed
    log.info("Caching backend help info")
    get_backend_help_info(cache=True)

    if "backend" not in running_containers:
        sleep(5)
        cmd("sparrow", "db", "check-schema")

    p.wait()
