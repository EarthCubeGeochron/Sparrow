import sys
import os
import click
from subprocess import Popen
from rich import print
from time import sleep

from sparrow_cli.upgrade_database import check_database_cluster_version
from sparrow_cli.util.exceptions import SparrowCommandError

from ..config.environment import validate_environment
from ..config import SparrowConfig
from ..util import compose, cmd, log
from ..config.command_cache import get_backend_help_info


def _report_image_versions():
    backend_img_version = os.environ.get("SPARROW_BACKEND_IMAGE")
    log.info(f"Backend image version: {backend_img_version}")

    frontend_img_version = os.environ.get("SPARROW_FRONTEND_IMAGE")
    log.info(f"Frontend image version: {frontend_img_version}")


def _get_prestart_script(cfg):
    if cfg.config_dir is None:
        return None
    prestart = cfg.config_dir / "sparrow-prestart.sh"
    if not prestart.exists():
        log.info(f"No prestart script found at {prestart}")
        return None
    return prestart


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

    _report_image_versions()
    # build containers
    if not cfg.offline:
        cmd("sparrow compose build")

    # Run the prebuild script
    prestart = _get_prestart_script(cfg)
    if prestart is not None:
        cmd("bash", str(prestart))

    version = check_database_cluster_version()
    print(f"Using PostgreSQL version {version}")
    if version <= 14:
        raise SparrowCommandError(
            "PostgreSQL version 14 or greater is required",
            details=f"Sparrow's database cluster is running PostgreSQL version {version}.",
        )

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
    get_backend_help_info(write_cache=True)

    if "backend" not in running_containers:
        sleep(5)
        cmd("sparrow", "db", "check-schema")

    p.wait()
