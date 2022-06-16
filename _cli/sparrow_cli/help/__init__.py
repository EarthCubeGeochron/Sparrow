import sys
import re
from click import style, Context
from click.formatting import HelpFormatter
from rich.text import Text
from os import environ
from pathlib import Path
from itertools import chain
from rich.console import Console
from ..util.formatting import format_config_path, format_description
from ..config import Level, SparrowConfig

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
        if name.startswith("sparrow-tasks-"):
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


def get_style(level: Level):
    if level == Level.SUCCESS:
        return "green"
    elif level == Level.WARNING:
        return "yellow"
    elif level == Level.ERROR:
        return "red"
    return None


class SparrowHelpFormatter(HelpFormatter):
    key_commands = {
        "up": "Start `sparrow` and follow logs",
        "down": "Safely stop `sparrow`",
        "info": "Show information about the installation",
        "create-test-lab": "Create an example installation of Sparrow",
        "run": "Run Sparrow tasks (alias to `sparrow tasks run`)",
    }

    config: SparrowConfig
    ctx: Context

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.config = self.ctx.find_object(SparrowConfig)
        super().__init__()

    def write_line(self, text=""):
        self.write(text + "\n")

    def flush(self, to=sys.stderr.write):
        to(self.getvalue())
        self.buffer = []

    def write_heading(self, heading):
        """Writes a heading into the buffer."""
        self.write(style(f"{'':>{self.current_indent}}{heading}", bold=True) + ":\n")

    def write_frontmatter(self):
        self.write_usage("sparrow", "[options] <command> [args]...")
        self.write_line()
        self.flush()
        cfg = environ.get("SPARROW_CONFIG", None)

        lines = []

        if self.config.lab_name is not None:
            lines.append(f"Lab name: [bold cyan]{self.config.lab_name}")

        if cfg is not None:
            d0 = format_config_path(self.config.config_file)
            lines.append(f"Config: [cyan]{d0}[/cyan]")

        if len(lines) == 0:
            return

        for line in lines:
            console.print(line)
        console.print("")

    def backend_help(self):
        # Grab commands file from backend
        commands = self.config.backend_commands
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

    def write_container_management(self, cli, core_commands):
        commands = command_dl(
            core_commands,
            extra_commands={
                "compose": "Alias to `docker-compose` that respects `sparrow` config",
                **{k: format_help(v) for k, v in command_info(self.ctx, cli)},
            },
        )

        self._write_section(
            "Container orchestration",
            {k: v for k, v in commands},
            skip=self.key_commands.keys(),
        )

    def _write_section(self, title, commands, skip=[]):
        _commands = {k: v for k, v in commands.items() if k not in skip}
        key_size = max([len(k) for k in _commands.keys()])
        with self.section(title):
            self.write_dl(_commands.items(), col_spacing=max([25 - key_size, 2]))
            self.write("\n")
        self.flush()

    def write_messages(self):
        if len(self.config.messages) == 0:
            return
        console.print("[bold]Status:")
        for message in self.config.messages:
            txt = Text.from_markup("• " + message.text)
            txt.style = get_style(message.level)
            console.print(txt)
            if message.details:
                console.print(f"  [dim]{message.details}[/dim]")
        console.print("")


sections = {
    "db": "Manage the `sparrow` database",
    "tasks": "Manage `sparrow`'s task system",
    "test": "Run `sparrow`'s test suite",
    "dev": "Helper commands for development",
    "docs": "Manage `sparrow`'s documentation",
}


def command_info(ctx, cli):
    for name in cli.list_commands(ctx):
        cmd = cli.get_command(ctx, name)
        if any([cmd.hidden, name in sections.keys(), name == "main"]):
            continue
        help = cmd.get_short_help_str()
        yield name, {"help": help, "plugin": None}


def echo_help(cli, ctx, core_commands=None, user_commands=None):
    # We want to run `sparrow up` first so we don't get surprised by container errors later
    # ...actually we likely don't want to do this. It seems like it pushes errors too early
    # in Sparrow's installation process
    # compose("up --no-start --remove-orphans")
    fmt = SparrowHelpFormatter(ctx)
    fmt.write_frontmatter()
    fmt.write_messages()
    fmt.write_section("Key commands", fmt.key_commands)
    fmt.write_section("Command groups", sections)

    fmt.backend_help()

    if user_commands is not None:
        lab_name = environ.get("SPARROW_LAB_NAME", "Lab-specific")
        fmt.write("[underline]" + lab_name + "[/underline] commands", user_commands)

    fmt.write_container_management(cli, core_commands)
