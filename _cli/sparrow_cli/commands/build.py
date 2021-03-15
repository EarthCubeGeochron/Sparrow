import click
from os import environ, chdir
from rich import print
from pathlib import Path
from json import load

from ..util import cmd

images_ = ["backend-base", "db-mysql-fdw", "backend", "frontend"]
ORG = "sparrowdata"


def root():
    return Path(environ["SPARROW_PATH"])


def get_image_info():
    # We should probably load version info from docker-compose files
    fp = root() / "sparrow-version.json"
    return load(fp.open("r"))["docker_images"]


@click.command(name="build")
@click.argument(
    "images", type=click.Choice(images_), required=False, default=None, nargs=-1
)
@click.option("--push", is_flag=True, default=False)
def sparrow_build(images, push=False):
    """Build Sparrow Docker images"""

    cfg = get_image_info()

    chdir(root())
    for image_name in images:
        im = cfg[image_name]
        version = im["version"]
        name = f"{ORG}/{image_name}:{version}"

        print(f"{image_name}: building image {name}")
        cmd("docker build -t", name, im["context"])
        if push:
            cmd("docker push ", name)
