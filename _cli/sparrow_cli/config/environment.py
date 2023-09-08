import sys
from os import environ, getenv
from rich import print
from typing import List

from macrostrat.utils import relative_path, get_logger
from .models import Message, Level

log = get_logger(__name__)


def is_defined(envvar):
    return environ.get(envvar) is not None


def is_truthy(envvar, default="False"):
    return getenv(envvar, "False").lower() in ("true", "1", "t", "y", "yes")


def prepare_docker_environment():
    if environ.get("_SPARROW_ENV_PREPARED", "0") == "1":
        return

    # Convey that we have already prepared the environment
    environ["_SPARROW_ENV_PREPARED"] = "1"

    # ENVIRONMENT VARIABLE DEFAULTS
    # Enable native builds and layer caching
    # https://docs.docker.com/develop/develop-images/build_enhancements/
    # This is kind of experimental
    environ.setdefault("COMPOSE_DOCKER_CLI_BUILD", "1")
    environ.setdefault("DOCKER_BUILDKIT", "1")

    # Set variables that might not be created in the config file
    # to default values
    # NOTE: much of this has been moved to `docker-compose.yaml`
    environ.setdefault("SPARROW_BASE_URL", "/")
    environ.setdefault("SPARROW_LAB_NAME", "")
    environ.setdefault("SPARROW_TASK_WORKER", "1")

    # Have to get rid of random printing to stdout in order to not break
    # logging and container ID
    # https://github.com/docker/scan-cli-plugin/issues/149
    # environ.setdefault("DOCKER_SCAN_SUGGEST", "false")
    environ.setdefault("DOCKER_CLI_HINTS", "false")


def prepare_compose_overrides(cfg) -> List[Message]:
    base = environ["SPARROW_PATH"]
    main = relative_path(base, "docker-compose.yaml")

    messages: List[Message] = []

    compose_files = [main]

    def add_override(name):
        fn = relative_path(base, "compose-overrides", f"docker-compose.{name}.yaml")
        compose_files.append(fn)

    env = environ.get("SPARROW_ENV", "development")
    environ.setdefault("SPARROW_ENV", "development")
    is_production = env == "production"

    # Use the docker-compose profile tool to enable some services
    # NOTE: this is a nicer way to do some things that needed to be handled by
    # compose-file overrides in the past.
    profiles = ["core", "frontend"]  # We default to always running the 'core' profile.
    if is_production:
        profiles.append("production")
    if is_truthy("SPARROW_TASK_WORKER"):
        profiles.append("task-worker")

    if cfg.local_frontend:
        profiles.remove("frontend")

    if len(profiles) > 0:
        # Only override profiles if they don't already exist in configuration.
        environ.setdefault("COMPOSE_PROFILES", ",".join(profiles))

    # Get profiles from environment
    profiles = environ.get("COMPOSE_PROFILES", "").split(",")
    log.info(f"docker-compose profiles: {profiles}")

    # Use SSL config if certain conditions are met
    desires_ssl = is_production and is_defined("SPARROW_DOMAIN")

    use_certbot = desires_ssl and is_defined("CERTBOT_EMAIL")
    use_custom_ssl = (
        desires_ssl
        and is_defined("SPARROW_CERTIFICATE")
        and is_defined("SPARROW_CERTIFICATE_KEY")
    )

    if use_certbot:
        # add_message("attempting to use Certbot for HTTPS")
        add_override("gateway.certbot-ssl")
        messages.append(
            Message(
                id="certbot-ssl",
                text="Using Certbot for SSL (https)",
                level=Level.SUCCESS,
            )
        )
    elif use_custom_ssl:
        # add_message("using custom SSL certificate")
        add_override("gateway.custom-ssl")
        messages.append(
            Message(
                id="custom-ssl",
                text="Using custom SSL (https) configuration",
                level=Level.SUCCESS,
            )
        )
    else:
        no_ssl_message = "To enable SSL (https), set a SPARROW_DOMAIN and either CERTBOT_EMAIL (for autoconfigured Certbot ssl) or SPARROW_CERTIFICATE + SPARROW_CERTIFICATE_KEY pointing to certificate files."
        if desires_ssl:
            messages.append(
                Message(
                    id="no-ssl",
                    text="SSL (https) is incorrectly configured",
                    details="You provided a SPARROW_DOMAIN configuration but no certificates. "
                    + no_ssl_message,
                    level=Level.ERROR,
                )
            )
        elif is_production:
            messages.append(
                Message(
                    id="no-ssl",
                    text="Using an insecure server in production",
                    details=no_ssl_message,
                    level=Level.WARNING,
                )
            )
        add_override("gateway.base")

    if is_production:
        add_override("production")

    if env == "development":
        add_override("development")

    # Overrides should now be formatted as a COMPOSE_FILE colon-separated list
    overrides = environ.get("SPARROW_COMPOSE_OVERRIDES", "")
    if overrides.startswith("-f "):
        messages.append(
            Message(
                id="old-overrides",
                text="You are using an old signature for the SPARROW_COMPOSE_OVERRIDES environment variable.",
                details="This option must now be formatted as a colon-separated path similar to the COMPOSE_FILE docker-compose configuration parameter (https://docs.docker.com/compose/reference/envvars/#compose_file)",
                level=Level.ERROR,
            )
        )
    elif overrides != "":
        compose_files += overrides.split(":")

    environ["COMPOSE_FILE"] = ":".join(str(c) for c in compose_files)
    log.info(f"Docker compose overrides: {compose_files}")
    return messages


def validate_environment():
    # Check for failing environment
    if environ.get("SPARROW_SECRET_KEY") is None:
        print(
            "[red]You [underline]must[/underline] set [bold]SPARROW_SECRET_KEY[/bold]. Exiting..."
        )
        sys.exit(1)
