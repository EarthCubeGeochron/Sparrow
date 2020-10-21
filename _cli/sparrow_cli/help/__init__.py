import sys
import re
import json
from click import style, secho
from click.formatting import HelpFormatter
from os import environ, path
from pathlib import Path
from itertools import chain
from rich.console import Console
from ..util import fail_without_docker, compose
from .backend import get_backend_command_help
from ..base import cli
from ..exc import SparrowCommandError

console = Console()

desc_regex = re.compile("^#\\s+Description:\\s+(.+)$")


def format_description(desc):
    desc = re.sub("\[\[(.*?)\]\]", style("\\1", fg="red", bold=True), desc)
    desc = re.sub("\[(.*?)\]", style("\\1", fg="green", bold=True), desc)
    return re.sub("`(.*?)`", style("\\1", fg="cyan"), desc)


def get_description(script):
    with open(script, "r") as f:
        for line in f:
            m = desc_regex.match(line)
            if m is not None:
                v = m.group(1)
                return format_description(v)
    return ""


def command_dl(directories: Path, extra_commands={}):
    # Add sparrow compose help separately
    # TODO: integrate into `click` to provide better help commands
    for cmd, help_text in extra_commands.items():
        yield (cmd, format_description(help_text))

    for f in chain(*(d.iterdir() for d in directories)):
        if not f.is_file():
            continue
        name = f.stem
        prefix = "sparrow-"
        if not name.startswith(prefix):
            continue
        if name.startswith("sparrow-db-"):
            continue
        if name.startswith("sparrow-docs-"):
            continue
        if name.startswith("sparrow-dev-"):
            continue
        yield (name[len(prefix) :], get_description(f).strip())


class SparrowHelpFormatter(HelpFormatter):
    def write_line(self, text=""):
        self.write(text + "\n")

    def flush(self, to=sys.stderr.write):
        to(self.getvalue())
        self.buffer = []


sections = {
    "db": "Manage the `sparrow` database",
    "test": "Run `sparrow`'s test suite",
    "docs": "Manage `sparrow`'s documentation",
    "dev": "Helper commands for development",
}


def format_config_path(cfg):
    """A helper for pretty formatting a path,
    eliding most of the directory tree.
    """
    home = path.expanduser("~")
    if cfg.startswith(home):
        cfg = cfg.replace(home, "~")
    split_path = cfg.split("/")
    tokens = []
    for i, token in enumerate(split_path):
        n_c = len(token)
        if i < len(split_path) - 2:
            tokens.append(token[0 : min(2, n_c)])
        else:
            tokens.append(token)
    return path.join(*tokens)


def backend_help(fmt):
    # Grab commands file from backend
    commands = get_backend_command_help()
    if commands is None:
        return
    with fmt.section("Backend"):
        fmt.write_dl(
            [(k, format_description(v)) for k, v in commands.items()], col_spacing=2
        )
        fmt.write("\n")
    fmt.flush()
    return fmt


def command_info(ctx, cli):
    for name in cli.list_commands(ctx):
        cmd = cli.get_command(ctx, name)
        if any([cmd.hidden, name in sections.keys(), name == "main"]):
            continue
        help = cmd.get_short_help_str()
        yield name, help


def echo_help(ctx, core_commands=None, user_commands=None):

    # We want to run `sparrow up` first so we don't get surprised by container errors later
    fail_without_docker()
    compose("up --no-start --remove-orphans")

    fmt = SparrowHelpFormatter()

    fmt.write_usage("sparrow", "[options] <command> [args]...")
    fmt.write_line()
    cfg = environ.get("SPARROW_CONFIG", None)
    if cfg is None:
        fmt.write_line(f"No configuration file found")
    else:
        d0 = format_config_path(cfg)
        fmt.write_line("Config: " + style(d0, fg="cyan"))
    d1 = style(environ.get("SPARROW_LAB_NAME", "None"), fg="cyan", bold=True)
    fmt.write_line(f"Lab: {d1}")
    fmt.flush()

    fmt.write("")

    with fmt.section("Command groups"):
        fmt.write_dl(
            [(k, format_description(v)) for k, v in sections.items()], col_spacing=20
        )
        fmt.write("\n")

    fmt.flush()

    fmt = backend_help(fmt)

    if user_commands is not None:
        lab_name = environ.get("SPARROW_LAB_NAME", "Lab-specific")
        fmt.write("[underline]" + lab_name + "[/underline] commands", user_commands)

    with fmt.section("Container management"):
        fmt.write_dl(
            command_dl(
                core_commands,
                extra_commands={
                    "compose": "Alias to `docker-compose` that respects `sparrow` config",
                    **{k: v for k, v in command_info(ctx, cli)},
                },
            ),
            col_spacing=9,
        )
    fmt.flush()
