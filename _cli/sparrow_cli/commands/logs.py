import click
from ..util import compose, container_id, cmd


@click.command(name="logs")
@click.argument("container", type=str, required=False, default=None)
def sparrow_logs(container):
    click.echo(container)
    if container is None:
        compose("logs --tail=0 --follow")
    else:
        id = container_id(container)
        # bail if multiline string
        cmd("docker logs -f", str(id))
