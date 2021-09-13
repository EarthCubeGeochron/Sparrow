import sys
import re
from click import style
from click.formatting import HelpFormatter
from os import environ
from pathlib import Path
from itertools import chain
from rich.console import Console
from .options_cache import get_backend_command_help, get_backend_help_info  # noqa
from ..util.shell import fail_without_docker
from ..util.formatting import format_config_path, format_description
from ..config import SparrowConfig

console = Console()

desc_regex = re.compile("^#\\s+Description:\\s+(.+)$")


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


def format_help(val, show_plugin=False):
    if isinstance(val, str):
        return val
    prefix = ""
    plugin = val.get("plugin")
    if show_plugin and plugin is not None:
        prefix = f"[{plugin}] "

    return prefix + val["help"]


def is_plugin_command(val):
    if isinstance(val, str):
        return False
    return val.get("plugin") is not None


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

    def write_heading(self, heading):
        """Writes a heading into the buffer."""
        self.write(style(f"{'':>{self.current_indent}}{heading}", bold=True) + ":\n")

    def write_frontmatter(self, ctx):
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

        ver = ctx.version_info
        if ver:
            msg2 = " "
            msg2 += "matches" if ver.is_match else "does not match"
            msg2 += " target "
            msg2 += style(ver.desired, underline=True)
            color = "green" if ver.is_match else "red"
            msg = "Sparrow "
            msg += "revision" if ver.uses_git else "version"
            msg += " "
            msg += style(ver.available, underline=True)
            msg += style(msg2, fg=color)
            self.write_line(style(msg, fg=color))

        self.flush()
        self.write("")

    def backend_help(self):
        # Grab commands file from backend
        commands = get_backend_command_help()
        if commands is None:
            return
        core_commands = {
            k: format_help(v) for k, v in commands.items() if not is_plugin_command(v)
        }
        plugin_commands = {
            k: format_help(v) for k, v in commands.items() if is_plugin_command(v)
        }
        self.write_section(
            "Core commands",
            core_commands,
            # These should be managed by subcommands...
            skip=[
                "db-migration",
                "remove-analytical-data",
                "remove-audit-trail",
                "db-update",
            ],
        )
        if len(plugin_commands) == 0:
            return
        self.write_section(
            "Plugin commands",
            plugin_commands,
            # These should be managed by subcommands...
        )

    def write_section(self, title, commands, **kwargs):
        commands = {k: format_description(v) for k, v in commands.items()}
        self._write_section(title, commands, **kwargs)

    def write_container_management(self, cli, ctx, core_commands):
        commands = command_dl(
            core_commands,
            extra_commands={
                "compose": "Alias to `docker-compose` that respects `sparrow` config",
                **{k: format_help(v) for k, v in command_info(ctx, cli)},
            },
        )
        self._write_section(
            "Container orchestration",
            {k: v for k, v in commands},
            skip=[*self.key_commands.keys()],
        )

    def _write_section(self, title, commands, skip=[]):
        _commands = {k: v for k, v in commands.items() if k not in skip}
        key_size = max([len(k) for k in _commands.keys()])
        with self.section(title):
            self.write_dl(_commands.items(), col_spacing=max([25 - key_size, 2]))
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
        yield name, {"help": help, "plugin": None}


def echo_help(cli, ctx, core_commands=None, user_commands=None):
    fail_without_docker()
    # We want to run `sparrow up` first so we don't get surprised by container errors later
    # ...actually we likely don't want to do this. It seems like it pushes errors too early
    # in Sparrow's installation process
    # compose("up --no-start --remove-orphans")

    fmt = SparrowHelpFormatter()
    fmt.write_frontmatter(ctx.find_object(SparrowConfig))
    fmt.write_section("Key commands", fmt.key_commands)
    fmt.write_section("Command groups", sections)

    fmt.backend_help()

    if user_commands is not None:
        lab_name = environ.get("SPARROW_LAB_NAME", "Lab-specific")
        fmt.write("[underline]" + lab_name + "[/underline] commands", user_commands)

    fmt.write_container_management(cli, ctx, core_commands)
