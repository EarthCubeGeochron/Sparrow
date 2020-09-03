import sys
import re
from click import echo, style, secho
from os import environ
from pathlib import Path
from rich import print
from itertools import chain
from rich.console import Console
from subprocess import PIPE, STDOUT
from click.formatting import HelpFormatter
from .util import compose

console = Console()

desc_regex = re.compile("^#\s+Description:\s+(.+)$")


def get_description(script):
    with open(script, "r") as f:
        for line in f:
            m = desc_regex.match(line)
            if m is not None:
                v = m.group(1)
                return re.sub("`(.*?)`", "[cyan]\\1[/cyan]", v)
    return ""


def cmd_help(title, directories: Path, extra_commands={}):
    echo("", err=True)
    print(title + ":", file=sys.stderr)

    # Add sparrow compose help separately
    # TODO: integrate into `click` to provide better help commands
    for cmd, help_text in extra_commands.items():
        echo("  {0:24}".format(cmd), err=True, nl=False)
        console.print(help_text, highlight=True)

    for f in chain(*(d.iterdir() for d in directories)):
        if not f.is_file():
            continue
        name = f.stem
        prefix = "sparrow-"
        if not name.startswith(prefix):
            continue
        if name.startswith("sparrow-db-"):
            continue

        echo("  {0:24}".format(name[len(prefix) :]), err=True, nl=False)
        desc = get_description(f)
        console.print(desc, highlight=True)


class SparrowHelpFormatter(HelpFormatter):
    def write_line(self, text=""):
        self.write(text + "\n")


def echo_help(core_commands=None, user_commands=None):
    fmt = SparrowHelpFormatter()

    fmt.write_usage("sparrow", "[options] <command> [args]...")
    fmt.write_line()
    d0 = style(environ.get("SPARROW_CONFIG", "None"), fg="cyan")
    fmt.write_line(f"Config: {d0}")
    d1 = style(environ.get("SPARROW_LAB_NAME", "None"), fg="cyan", bold=True)
    fmt.write_line(f"Lab: {d1}")

    sys.stderr.write(fmt.getvalue())

    # Note: TTY flag (-T) has issues on older versions of docker-compose (<~1.23).
    # We solve this by bundling a newer version of docker-compose.
    out = compose("run --no-deps -T backend sparrow", stdout=PIPE, stderr=STDOUT)
    if out.returncode != 0:
        secho("Could not access help text for the Sparrow backend", err=True, fg="red")
    else:
        echo(b"\n".join(out.stdout.splitlines()[1:]), err=True)

    if user_commands is not None:
        lab_name = environ.get("SPARROW_LAB_NAME", "Lab-specific")
        cmd_help("[underline]" + lab_name + "[/underline] commands", user_commands)

    cmd_help(
        "Container management commands",
        core_commands,
        extra_commands={
            "compose": "Alias to [cyan]docker-compose[/cyan] that respects [cyan]sparrow[/cyan] config",
            "test": "Run sparrow's testing suite.",
        },
    )
