from click import group
from os import environ, path
from ..group import CommandGroup
from ..util import compose

# Commands inherited from earlier shell version of CLI.
shell_commands = {
    "build": "[Production]: Build the documentation static site",
    "run": "[Production]: Run the documentation site",
    "up": "Bring up a testing documentation website",
    "test": "Confirm that the documentation website is live",
}


@group(name="docs", cls=CommandGroup)
def sparrow_docs():
    pass


for k, v in shell_commands.items():
    sparrow_docs.add_shell_command(k, v, prefix="sparrow-docs-")


@sparrow_docs.command("down")
def docs_down():
    """Bring down the documentation website"""
    # Move work to another directory
    work_dir = path.join(environ["SPARROW_PATH"], "docs")
    docs_compose = path.join(work_dir, "docker-compose.yaml")
    env = dict(**environ)
    env["COMPOSE_FILE"] = docs_compose
    env["COMPOSE_PROJECT_NAME"] = "sparrow_docs"
    compose("down", env=env, cwd=work_dir)
