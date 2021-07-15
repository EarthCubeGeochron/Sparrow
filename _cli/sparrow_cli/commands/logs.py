import click
from ..util import compose, container_id, cmd, log


@click.command(name="logs")
@click.argument("container", type=str, required=False, default=None)
def sparrow_logs(container):
    if container is None:
        log.debug(f"Following logs for all containers")
        compose("logs --tail=0 --follow")
    else:
        log.debug(f"Following logs for container {container}")
        id = container_id(container)
        # bail if multiline string
        cmd("docker logs -f", str(id))
