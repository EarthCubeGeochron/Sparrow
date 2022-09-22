"""
Scripts for upgrading the database cluster if it is out of date.
"""
from .util.shell import compose
from rich import print


def check_database_cluster_version():
    """
    Check the version of a PostgreSQL cluster in a Docker volume
    under a managed installation of Sparrow.
    """
    res = compose(
        "run",
        "--rm",
        "db",
        "cat",
        "/var/lib/postgresql/data/PG_VERSION",
        capture_output=True,
    )
    return int(res.stdout.decode("utf-8").strip())


version_images = {
    11: "mdillon/postgis:11",
    14: "postgis/postgis:14-3.3",
}


def upgrade_database_cluster(current_version, desired_version):
    """
    Upgrade a PostgreSQL cluster in a Docker volume
    under a managed installation of Sparrow.
    """
    if current_version == desired_version:
        print("Database cluster is already up to date.")
        return

    if current_version not in version_images:
        raise ValueError(f"Unsupported database cluster version: {current_version}")

    if desired_version not in version_images:
        raise ValueError(f"Unsupported database cluster version: {desired_version}")

    print(
        f"Upgrading database cluster from version {current_version} to {desired_version}..."
    )

    # Stop the database
    compose("stop", "db")

    # Remove the database container
    compose("rm", "-f", "db")

    # Remove the database volume
    compose("volume", "rm", "sparrow_db")

    # Start the database
    compose("up", "-d", "db")

    # Wait for the database to be ready
    compose("run", "--rm", "db", "wait-for-it", "db:5432", "--", "true")

    print("Database cluster upgraded successfully.")
