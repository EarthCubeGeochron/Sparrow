import click
from ..util import compose, container_id, cmd, log


@click.command(name="logs")
@click.argument("container", type=str, required=False, default=None)
def sparrow_logs(container):
    if container is not None and container.strip() != "":
        id = container_id(container)
        # bail if multiline string
        if "\\n" not in id:
            log.debug(f"Following logs for container {container}")
            return cmd("docker logs -f", str(id))
    log.debug(f"Following logs for all containers")
    compose("logs --tail=0 --follow")
