import click
from os import environ, path, chdir
import subprocess

@click.command("system-prune")
@click.option("--volume", default=False, help="prune sparrow volumes as well (bool)")
def sparrow_docker_prune(volume):
    lab_name = environ.get("SPARROW_LAB_NAME").lower()
    if volume:
        prompt = "This method will drop the data volumes including the database! To continue type, 'I'm positive.'"
        ans = click.prompt(prompt)
        if ans == "I'm positive.":
            click.echo("pruning sparrow volumes!!")
            filter_arg = f" | grep '{lab_name}*')"
            volume_cmd = "docker volume rm $(docker volume ls --format '{{.Name}}'" + filter_arg
            click.echo(volume_cmd)
            subprocess.call(volume_cmd,shell=True)
    else:
        click.echo("pruning sparrow system excpet volumes")
        filter_arg = f" | grep '{lab_name}*')"
        img_cmd = "docker image rm $(docker image ls --format '{{.Repository}}'" + filter_arg
        click.echo(img_cmd)
        subprocess.call(img_cmd, shell=True)