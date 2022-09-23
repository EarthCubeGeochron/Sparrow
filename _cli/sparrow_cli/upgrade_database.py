"""
Scripts for upgrading the database cluster if it is out of date.
"""
from contextlib import contextmanager
from os import environ
from pathlib import Path
from .config import SparrowConfig
from .util.exceptions import SparrowCommandError
from .util.shell import compose, cmd
from rich import print
from rich.console import Console
from docker import from_env
from docker.models.containers import Container
import time
from datetime import datetime
import subprocess
from subprocess import Popen

environ.setdefault("DOCKER_HOST", "unix:///var/run/docker.sock")

client = from_env()

console = Console()


def check_database_cluster_version(volume_name: str):
    """
    Check the version of a PostgreSQL cluster in a Docker volume
    under a managed installation of Sparrow.
    """
    cluster_dir = "/var/lib/postgresql/data"
    version_file = Path(cluster_dir) / "PG_VERSION"
    stdout = client.containers.run(
        "bash",
        f"cat {version_file}",
        volumes={volume_name: {"bind": cluster_dir, "mode": "ro"}},
        remove=True,
        stdout=True,
    )
    return int(stdout.decode("utf-8").strip())


version_images = {11: "mdillon/postgis:11", 14: "postgis/postgis:14-3.3"}


def database_cluster_version(cfg: SparrowConfig):
    cluster_volume_name = cfg.project_name + "_db_cluster"
    return check_database_cluster_version(cluster_volume_name)


def check_database_version(cfg: SparrowConfig):
    cluster_volume_name = cfg.project_name + "_db_cluster"
    version = check_database_cluster_version(cluster_volume_name)
    upgrade_text = " No upgrade path is available — perhaps you have downgraded your Sparrow installation?"
    if version < cfg.postgres_version and version_images[version] is not None:
        upgrade_text = " Run [cyan]sparrow db update[/cyan] to upgrade the database."
    if version < cfg.postgres_version:
        raise SparrowCommandError(
            f"PostgreSQL version {cfg.postgres_version} is required",
            details=f"Sparrow's database cluster is running PostgreSQL version {version}."
            + upgrade_text,
        )
    else:
        print(f"Using PostgreSQL version {version}")


def wait_for_cluster(container: Container):
    """
    Wait for a database to be ready.
    """
    print("Waiting for database to be ready...")
    # is_running = False
    # while not is_running:
    #     print(container.status)
    #     time.sleep(0.1)
    #     is_running = container.status == "created"

    is_ready = False
    while not is_ready:
        time.sleep(0.1)
        log_step(container)
        res = container.exec_run("pg_isready")
        is_ready = res.exit_code == 0
    return


_log_tracker = {}


def log_step(container: Container):
    last_step = _log_tracker.get(container.id, None)
    for line in container.logs(since=last_step).splitlines():
        console.print(line.decode("utf-8"), style="dim")
    _log_tracker[container.id] = datetime.now()


@contextmanager
def database_cluster(
    image: str, data_volume: str, remove=True, environment=None
) -> Container:
    """do
    Start a database cluster in a Docker volume
    under a managed installation of Sparrow.
    """
    print("Starting database cluster...")
    try:
        container = client.containers.run(
            image,
            detach=True,
            environment=environment,
            volumes={data_volume: {"bind": "/var/lib/postgresql/data", "mode": "rw"}},
        )
        wait_for_cluster(container)
        yield container
    finally:
        print(f"Stopping database cluster {image}...")
        container.stop()
        if remove:
            print(f"Removing database cluster for image {image}...")
            container.remove()


def check_database_exists(container: Container, db_name: str) -> bool:
    res = container.exec_run(f"psql -U postgres -lqt", stdout=True, demux=True)
    stdout = res.output[0].decode("utf-8")
    for line in stdout.splitlines():
        if line.split("|")[0].strip() == db_name:
            return True
    return False


def count_database_tables(container: Container, db_name: str) -> int:
    res = container.exec_run(
        f"psql -U postgres -d {db_name} -c 'SELECT COUNT(*) FROM information_schema.tables;'",
        stdout=True,
        demux=True,
    )
    stdout = res.output[0].decode("utf-8")
    return int(stdout.splitlines()[2].strip())


def replace_docker_volume(old_name: str, new_name: str):
    """
    Replace the contents of a Docker volume.
    """
    print(f"Moving contents of volume {old_name} to {new_name}")
    client.containers.run(
        "bash",
        "mv /old /new",
        volumes={old_name: {"bind": "/old"}, new_name: {"bind": "/new"}},
        remove=True,
    )


def upgrade_database_cluster(cfg: SparrowConfig):
    """
    Upgrade a PostgreSQL cluster in a Docker volume
    under a managed installation of Sparrow.
    """
    current_version = database_cluster_version(cfg)
    if current_version == cfg.postgres_version:
        print("Database cluster is already up to date.")
        return

    if current_version not in version_images:
        raise SparrowCommandError("No upgrade path available")

    if cfg.postgres_version not in version_images:
        raise SparrowCommandError("Target PostgreSQL version is not supported")

    cluster_volume_name = cfg.project_name + "_db_cluster"
    cluster_new_name = cfg.project_name + "_db_cluster_new"

    # Create the volume for the new cluster
    client.volumes.get(cluster_new_name).remove(force=True)
    dest_volume = client.volumes.create(name=cluster_new_name)

    print(
        f"Upgrading database cluster from version {current_version} to {cfg.postgres_version}..."
    )

    # Stop the database
    compose("stop", "db")

    with database_cluster(
        version_images[current_version], cluster_volume_name
    ) as source, database_cluster(
        version_images[cfg.postgres_version],
        dest_volume.name,
        environment={"POSTGRES_HOST_AUTH_METHOD": "trust"},
    ) as target:
        # Dump the database

        # Check if the database exists
        dbname = "sparrow"
        if check_database_exists(source, dbname):
            print(f"Database {dbname} exists in source cluster")
        else:
            print(f"Database {dbname} does not exist in source, skipping dump.")
            return

        n_tables = count_database_tables(source, dbname)

        log_step(target)

        print("Dumping database...")

        res = source.exec_run(
            "pg_dump -Fc -U postgres sparrow",
            stream=True,
            stdout=True,
            stderr=True,
            demux=True,
        )

        target.exec_run("createdb -U postgres sparrow")

        process = Popen(
            (
                "docker",
                "exec",
                "-i",
                target.name,
                "pg_restore",
                "-U",
                "postgres",
                "-d",
                "sparrow",
            ),
            stdin=subprocess.PIPE,
        )

        with process.stdin as pipe:
            nbytes = 0
            for i, (stdout, stderr) in enumerate(res.output):
                if stderr is not None:
                    print()
                    print(stderr.decode("utf-8"))
                nbytes += len(stdout)
                pipe.write(stdout)
                print(f"Dumped {nbytes/1_000_000} MB        ", end="\r")
            pipe.flush()

        db_exists = check_database_exists(target, dbname)
        new_n_tables = count_database_tables(target, dbname)

        if db_exists:
            print(f"Database {dbname} exists in target cluster.")
        else:
            print(f"Database {dbname} does not exist in target, dump failed.")
            dest_volume.remove()
            return

        if new_n_tables >= n_tables:
            print(f"{new_n_tables} tables were restored.")
        else:
            print(f"Expected {n_tables} tables, got {new_n_tables}")
            console.print("The migration failed.", style="bold red")
            dest_volume.remove()
            return

    # Remove the old volume
    backup_volume_name = cluster_volume_name + "_backup"
    console.print(f"Backing up old volume to {backup_volume_name}", style="bold")
    client.volumes.get(backup_volume_name).remove(force=True)
    client.volumes.create(name=backup_volume_name)
    replace_docker_volume(cluster_volume_name, backup_volume_name)

    console.print(
        f"Moving contents of new volume to {cluster_volume_name}", style="bold"
    )
    replace_docker_volume(cluster_new_name, cluster_volume_name)
    client.volumes.get(cluster_new_name).remove(force=True)

    console.print("Done!", style="bold green")
