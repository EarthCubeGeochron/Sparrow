import sys
import re
import json
from click import style, secho
from click.formatting import HelpFormatter
from os import environ, path
from pathlib import Path
from itertools import chain
from rich.console import Console
from ..util import cmd, fail_without_docker, compose
from .backend import get_backend_command_help
from ..base import cli
from ..exc import SparrowCommandError
from .util import format_config_path

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
        key = name[len(prefix) :]
        yield (key, get_description(f).strip())


class SparrowHelpFormatter(HelpFormatter):
    key_commands = {
        "up": "Start `sparrow` and follow logs",
        "down": "Safely stop `sparrow`",
        "info": "Show information about the installation",
        "create-test-lab": "Create an example installation of Sparrow",
    }

    def write_line(self, text=""):
        self.write(text + "\n")

    def flush(self, to=sys.stderr.write):
        to(self.getvalue())
        self.buffer = []

    def write_frontmatter(self):
        self.write_usage("sparrow", "[options] <command> [args]...")
        self.write_line()
        cfg = environ.get("SPARROW_CONFIG", None)
        if cfg is None:
            self.write_line(f"No configuration file found")
        else:
            d0 = format_config_path(cfg)
            self.write_line("Config: " + style(d0, fg="cyan"))
        d1 = style(environ.get("SPARROW_LAB_NAME", "None"), fg="cyan", bold=True)
        self.write_line(f"Lab: {d1}")
        self.flush()
        self.write("")

    def backend_help(self):
        # Grab commands file from backend
        commands = get_backend_command_help()
        if commands is None:
            return
        self.write_section("Backend", commands)

    def write_section(self, title, commands, **kwargs):
        commands = {k: format_description(v) for k, v in commands.items()}
        self._write_section(title, commands, **kwargs)

    def write_container_management(self, ctx, core_commands):
        commands = command_dl(
            core_commands,
            extra_commands={
                "compose": "Alias to `docker-compose` that respects `sparrow` config",
                **{k: v for k, v in command_info(ctx, cli)},
            },
        )
        self._write_section(
            "Container management",
            {k: v for k, v in commands},
            skip=[*self.key_commands.keys()],
        )

    def _write_section(self, title, commands, skip=[]):
        with self.section(title):
            _items = [(k, v) for k, v in commands.items() if k not in skip]
            self.write_dl(_items, col_spacing=10)
            self.write("\n")
        self.flush()


sections = {
    "db": "Manage the `sparrow` database",
    "test": "Run `sparrow`'s test suite",
    "docs": "Manage `sparrow`'s documentation",
    "dev": "Helper commands for development",
}


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
    fmt.write_frontmatter()
    fmt.write_section("Key commands", fmt.key_commands)
    fmt.write_section("Command groups", sections)

    fmt.backend_help()

    if user_commands is not None:
        lab_name = environ.get("SPARROW_LAB_NAME", "Lab-specific")
        fmt.write("[underline]" + lab_name + "[/underline] commands", user_commands)

    fmt.write_container_management(ctx, core_commands)
