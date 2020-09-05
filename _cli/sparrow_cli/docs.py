from .base import cli
from .group import CommandGroup

# Commands inherited from earlier shell version of CLI.
shell_commands = {
    "build": "[Production]: Build the documentation static site",
    "run": "[Production]: Run the documentation site",
    "up": "Bring up a testing documentation website",
    "test": "Confirm that the documentation website is live",
}


@cli.group(name="docs", cls=CommandGroup)
def sparrow_docs():
    pass


for k, v in shell_commands.items():
    sparrow_docs.add_shell_command(k, v, prefix="sparrow-docs-")
