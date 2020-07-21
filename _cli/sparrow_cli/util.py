from os import environ, chdir, path
from subprocess import run, PIPE, STDOUT
from shlex import split
from click import secho


def cmd(*v, **kwargs):
    val = " ".join(v)
    return run(split(val), **kwargs)


def compose(*args, **kwargs):
    base = environ["SPARROW_PATH"]
    main = path.join(base, "docker-compose.yaml")

    compose_files = [main]

    env = environ.get("SPARROW_ENV", "production")
    if env == "production":
        compose_files.append(path.join(base, "docker-compose.production.yaml"))

        if environ.get("CERTBOT_EMAIL") is not None:
            # We want to use certbot NGINX configuration
            compose_files.append(path.join(base, "docker-compose.certbot.yaml"))

    # Overrides should now be formatted as a COMPOSE_FILE colon-separated list
    overrides = environ.get("SPARROW_COMPOSE_OVERRIDES", "")
    if overrides.startswith("-f "):
        secho(
            "You are using a deprecated signature for the SPARROW_COMPOSE_OVERRIDES "
            "environment variable. This option should now be formatted as a "
            "colon-separated path similar to the COMPOSE_FILE docker-compose "
            "configuration parameter (https://docs.docker.com/compose/reference/envvars/#compose_file)",
            fg="yellow",
            err=True,
        )
    elif overrides != "":
        compose_files += overrides.split(":")

    environ["COMPOSE_FILE"] = ":".join(compose_files)

    chdir(base)
    return cmd("docker-compose", overrides, *args, **kwargs)


def container_is_running(name):
    res = compose("exec", name, "true", stdout=PIPE, stderr=STDOUT)
    return res.returncode == 0
