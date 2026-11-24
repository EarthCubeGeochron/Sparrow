"""
Named environments for the command line, from a `sparrow.toml` at or above the
working directory. Each table describes one lab, or one deployment of it:

    [default]
    lab_name = "Example lab"

    [production]
    env_class = "production"
    api = "https://sparrow.example.org"
    api_token = "op://Lab/Sparrow/token"

`SPARROW_ENV` names the environment in use. It was always `development` or
`production`; those still work with no file at all, and any other environment
says which of the two it is with `env_class`.

`sparrow-config.sh` is still read where it exists; it describes the server a
lab runs on, and its variables take precedence there.
"""

from os import environ
from typing import Optional

from macrostrat.app_frame.environments import Environments
from macrostrat.app_frame.secrets import Secret


class SparrowEnvironments(Environments):
    # SPARROW_CONFIG is already the path of sparrow-config.sh
    config_var = property(lambda self: "SPARROW_TOML", lambda self, v: None)


# Environment names that say their own class, as SPARROW_ENV always has
_class_names = ("local", "development", "staging", "production")


def environment_class(environments: Environments) -> str:
    """Where the active environment sits, from laptop to production."""
    env = environments.env
    if environments.settings.get("env_class") is not None:
        return environments.env_class.value
    if env is None:
        # Nothing chosen: a lab being worked on, as before
        return "development"
    if env in _class_names:
        return env
    return "production"


def service_mode(environments: Environments) -> str:
    """What the lab's services are told: they know only two ways to run."""
    if environment_class(environments) in ("local", "development"):
        return "development"
    return "production"


def load_environments(env: Optional[str] = None) -> Environments:
    if env is not None:
        environ["SPARROW_ENV"] = env
        environ.pop("SPARROW_ENV_EXPIRES", None)
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
