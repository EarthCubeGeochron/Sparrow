import click
from os import environ
from subprocess import Popen


def space(spaces=1):
    for i in range(0, spaces):
        click.echo("")


@click.command("system-prune")
@click.option("--volume", default=False, help="prune sparrow volumes as well (bool)")
def sparrow_docker_prune(volume):
    lab_name = environ.get("COMPOSE_PROJECT_NAME").lower()
    if len(lab_name) == 0:
        click.secho("No compose project name environment variable set!", fg="red")
    elif volume:
        space()
        prompt1 = "This method will drop the data volumes including the database!"
        prompt2 = "If you don't want to loose data, backup the database first."

        click.secho(prompt1, fg="red")
        click.secho(prompt2, fg="red")
        space()
        ans = click.prompt("To continue type, 'I'm positive.'")
        space()
        if ans == "I'm positive.":
            click.secho(f"Deleting volumes associated to {lab_name}", fg="yellow")
            filter_arg = f" | grep '{lab_name}*')"
            volume_cmd = (
                "docker volume rm $(docker volume ls --format '{{.Name}}'" + filter_arg
            )
            p = Popen(volume_cmd, shell=True)
            p.wait()
            click.secho("Volumes deleted", fg="green")
        else:
            click.secho("Good Choice", fg="green")
            click.secho("Aborting...", fg="red")

    else:
        space()
        click.secho(f"Removing images associated with {lab_name}", fg="yellow")
        filter_arg = f" | grep '{lab_name}*')"
        img_cmd = (
            "docker image rm $(docker image ls --format '{{.Repository}}'" + filter_arg
        )
        p = Popen(img_cmd, shell=True)
        p.wait()
        click.secho("Images successfully removed", fg="green")
