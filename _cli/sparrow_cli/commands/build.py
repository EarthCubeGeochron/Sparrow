import click
from os import environ, chdir

from click import pass_context
from rich import print
from pathlib import Path
from json import load

from ..context import SparrowConfig
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
@pass_context
def sparrow_build(ctx, images, push=False):
    """Build Sparrow Docker images"""

    cfg = ctx.find_object(SparrowConfig)

    # get version info
    versions = get_image_info()

    chdir(root())
    for image_name in images:
        im = versions[image_name]
        version = im.get("version")
        if version == "@core":
            # For this image we are specifying a version tied to the
            # canonical Sparrow backend version. This might not be the
            # ideal thing to do but it seems to work OK...
            version = cfg.find_sparrow_version()
        name = f"{ORG}/{image_name}:{version}"

        print(f"{image_name}: building image {name}")
        # Allow build to be used for layer cache
        # https://github.com/moby/moby/issues/39003
        cmd(
            "docker build -t",
            name,
            "--build-arg BUILDKIT_INLINE_CACHE=1",
            im["context"],
        )
        if push:
            cmd("docker push ", name)
