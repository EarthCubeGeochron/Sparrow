import click
from os import environ, path, chdir
from pathlib import Path
from ..util import cmd


# Ideally this would be a subcommand, not its own separate command
@click.command("create-test-lab")
@click.argument("directory", type=click.Path())
def sparrow_test_lab(directory):
    """Create a configuration directory for a test lab"""
    fp = path.join(environ["SPARROW_PATH"], "test-lab")
    click.echo(f"Making a test lab setup in directory {directory}")
    cmd("rsync -av", fp + "/", str(directory) + "/")
    chdir(directory)
    gitdir = Path(".git")
    if not gitdir.is_dir():
        click.echo(f"Setting up git version control")
        cmd("git init .")
        cmd("git add .")
        cmd("git commit -m 'Initial commit'")
