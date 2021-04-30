import click
from ..util import cmd, container_id


@click.command()
@click.argument("container", type=str, default="backend")
def sparrow_attach(container="backend"):
    """Attach to the standard output of a container"""
    id = container_id(container)
    click.echo(f"Attaching to sparrow {container}", err=True)
    cmd("docker attach", id)
