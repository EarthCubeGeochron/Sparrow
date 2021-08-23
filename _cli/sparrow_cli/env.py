import sys
from os import environ, path
from click import secho
from rich import print
from sparrow_utils import relative_path


def prepare_docker_environment():
    if environ.get("_SPARROW_ENV_PREPARED", "0") == "1":
        return
    # Convey that we have already prepared the environment
    environ["_SPARROW_ENV_PREPARED"] = "1"

    # ENVIRONMENT VARIABLE DEFAULTS
    # Set variables that might not be created in the config file
    # to default values
    # NOTE: much of this has been moved to `docker-compose.yaml`
    environ.setdefault("SPARROW_BASE_URL", "/")
    environ.setdefault("SPARROW_LAB_NAME", "")
    environ.setdefault("SPARROW_TASK_WORKER", "1")

    # Have to get rid of random printing to stdout in order to not break
    # logging and container ID
    # https://github.com/docker/scan-cli-plugin/issues/149
    environ.setdefault("DOCKER_SCAN_SUGGEST", "false")

    prepare_compose_overrides()


def is_defined(envvar):
    return environ.get(envvar) is not None


def is_truthy(envvar, default="0"):
    return environ.get(envvar, default).lower() not in ["0", "false", "no"]


def prepare_compose_overrides():
    base = environ["SPARROW_PATH"]
    main = relative_path(base, "docker-compose.yaml")
    compose_files = [main]

    def add_override(name):
        fn = relative_path(base, "compose-overrides", f"docker-compose.{name}.yaml")
        compose_files.append(fn)

    env = environ.get("SPARROW_ENV", "development")
    is_production = env == "production"

    # Use the docker-compose profile tool to enable some services
    # NOTE: this is a nicer way to do some things that needed to be handled by
    # compose-file overrides in the past.
    profiles = []
    if is_production:
        profiles.append("production")
    if is_truthy("SPARROW_TASK_WORKER"):
        profiles.append("task-worker")

    if len(profiles) > 0:
        environ["COMPOSE_PROFILES"] = ",".join(profiles)

    # Use certbot for SSL if certain conditions are met
    use_certbot = (
        is_production and is_defined("CERTBOT_EMAIL") and is_defined("SPARROW_DOMAIN")
    )

    if use_certbot:
        # add_message("attempting to use Certbot for HTTPS")
        add_override("certbot")
    else:
        add_override("base")

    if is_production:
        add_override("production")

    if env == "development":
        add_override("development")

    # Overrides should now be formatted as a COMPOSE_FILE colon-separated list
    overrides = environ.get("SPARROW_COMPOSE_OVERRIDES", "")
    if overrides.startswith("-f "):
        secho(
            "You are using an old signature for the SPARROW_COMPOSE_OVERRIDES "
            "environment variable. This option must now be formatted as a "
            "colon-separated path similar to the COMPOSE_FILE docker-compose "
            "configuration parameter (https://docs.docker.com/compose/reference/envvars/#compose_file)",
            fg="red",
            err=True,
        )
    elif overrides != "":
        compose_files += overrides.split(":")

    environ["COMPOSE_FILE"] = ":".join(compose_files)


def validate_environment():
    # Check for failing environment
    if environ.get("SPARROW_SECRET_KEY") is None:
        print(
            "[red]You [underline]must[/underline] set [bold]SPARROW_SECRET_KEY[/bold]. Exiting..."
        )
        sys.exit(1)
