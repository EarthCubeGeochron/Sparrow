"""
Named environments for the command line, from a `sparrow.toml` at or above the
working directory. Each table describes one lab, or one deployment of it:

    [default]
    lab_name = "Example lab"

    [production]
    env_class = "production"
    api = "https://sparrow.example.org"
    api_token = "op://Lab/Sparrow/token"

`sparrow-config.sh` is still read where it exists; it describes the server a
lab runs on, and its variables take precedence there.
"""

from os import environ
from typing import Optional

from macrostrat.app_frame.environments import Environments
from macrostrat.app_frame.secrets import Secret


class SparrowEnvironments(Environments):
    # SPARROW_ENV and SPARROW_CONFIG already mean the backend's mode and the
    # path of sparrow-config.sh, so the selection variables take other names.
    env_var = property(lambda self: "SPARROW_ENVIRONMENT", lambda self, v: None)
    expires_var = property(
        lambda self: "SPARROW_ENVIRONMENT_EXPIRES", lambda self, v: None
    )
    config_var = property(lambda self: "SPARROW_TOML", lambda self, v: None)


def load_environments(env: Optional[str] = None) -> Environments:
    if env is not None:
        environ["SPARROW_ENVIRONMENT"] = env
        environ.pop("SPARROW_ENVIRONMENT_EXPIRES", None)
    # --env is an option of `sparrow` itself; `-e` belongs to wrapped commands
    return SparrowEnvironments.for_command_line(
        "sparrow", config_name="sparrow.toml", read_argv=False
    )


def export_settings(environments: Environments):
    """Give the settings of the active environment to the commands this one
    runs, as SPARROW_* variables. Variables already set are left alone, and a
    secret is never exported: it is fetched by the command that needs it."""
    if environments.config_file is None:
        return
    for key in environments.settings:
        value = environments.settings.get(key)
        if isinstance(value, (Secret, dict)) or value is None:
            continue
        if isinstance(value, bool):
            value = "1" if value else "0"
        environ.setdefault("SPARROW_" + key.upper(), str(value))
