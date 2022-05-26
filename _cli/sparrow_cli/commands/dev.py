from click import group, pass_obj
from rich import print
from ..release_generation import create_release, check_version
from ..util import CommandGroup, compose


# Commands inherited from earlier shell version of CLI.
shell_commands = {
    "graph": "Graph the git commit history of the Sparrow repository",
    "local": "Run sparrow with a locally-installed frontend (this can be less resource-intensive)",
}


@group(name="dev", cls=CommandGroup)
def sparrow_dev():
    pass


for k, v in shell_commands.items():
    sparrow_dev.add_shell_command(k, v, prefix="sparrow-dev-")

sparrow_dev.add_command(create_release)
sparrow_dev.add_command(check_version)


@sparrow_dev.command(name="reload")
def dev_reload():
    """Reload the web browser when the app is in development mode"""
    compose("exec frontend /app/node_modules/.bin/browser-sync reload")


@sparrow_dev.command(name="clear-cache")
def clear_cache():
    """Clear caches used by the command-line application"""
    from ..config.command_cache import cli_cache_file

    cache = cli_cache_file()
    cache.unlink(missing_ok=True)
    print(f"Cleared cache file {cache}")

    # Clear backend SQLAlchemy cache
    backend_cache = "/root/.sqlalchemy-cache/sparrow-db-cache.pickle"
    compose("run --no-deps backend rm -f", backend_cache)
    print(f"Cleared SQLAlchemy cache {backend_cache} in backend container")


@sparrow_dev.command(name="print-config")
@pass_obj
def print_config(ctx):
    """Print the Sparrow CLI configuration object"""
    print(ctx)
