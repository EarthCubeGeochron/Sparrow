"""
A lab's configuration, in a `sparrow.toml` at or above the working directory
(or named by `SPARROW_CONFIG`). Each table is an environment: one lab, or one
deployment of it.

    [default]
    lab_name = "Example lab"
    data_dir = "./data"

    [development]
    secret_key = "not a real secret, for a laptop"

    [production]
    domain = "sparrow.example.org"
    secret_key = "op://Lab/Sparrow/secret-key"
    api = "https://sparrow.example.org"
    api_token = "op://Lab/Sparrow/token"
    database = "op://Lab/Sparrow/database-url"

A setting reaches the lab's services as the `SPARROW_*` variable of the same
name, so anything `sparrow-config.sh` exported can be written here instead.
`SPARROW_ENV` names the environment in use. It was always `development` or
`production`; those still work with no file at all, and any other environment
says which of the two it is with `env_class`.

`sparrow-config.sh` is still sourced where it exists, and what it exports
takes precedence.
"""

from os import environ
from typing import Optional

from macrostrat.app_frame.environments import Environments
from macrostrat.app_frame.secrets import Secret, SecretResolutionError

from ..util.exceptions import SparrowCommandError

# Settings that steer the command line rather than the lab's services
_own_keys = ("env_class", "confirm", "active_ttl", "write_gate", "op_account")

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
    environments = Environments.for_command_line(
        "sparrow", config_name="sparrow.toml", read_argv=False
    )
    if environments.config_file is not None:
        # For the commands this one runs, and for files a lab keeps beside it
        environ["SPARROW_CONFIG"] = str(environments.config_file)
        environ.setdefault("SPARROW_CONFIG_DIR", str(environments.config_file.parent))
    return environments


def _as_variable(environments: Environments, key: str, value) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, str) and value.startswith(("./", "../")):
        # Paths are written relative to the file that names them
        return str(environments.settings.path(key).resolve())
    return str(value)


def export_settings(environments: Environments, secrets: bool = False):
    """Give the active environment's settings to the commands this one runs,
    as SPARROW_* variables. Variables already set are left alone. A secret is
    fetched only when `secrets` is asked for: by commands that run the lab."""
    if environments.config_file is None:
        return
    for key in environments.settings:
        if key in _own_keys:
            continue
        name = "SPARROW_" + key.upper()
        if name in environ:
            continue
        value = environments.settings.get(key)
        if value is None or isinstance(value, dict):
            continue
        if isinstance(value, Secret):
            if not secrets:
                continue
            try:
                value = value.get()
            except SecretResolutionError as err:
                raise SparrowCommandError(
                    f"Could not fetch the secret for `{key}`",
                    details=f"{err}\nNamed in {environments.config_file}",
                )
        environ[name] = _as_variable(environments, key, value)
