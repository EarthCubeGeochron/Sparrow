"""
Scripts for upgrading the database cluster if it is out of date.
"""
from contextlib import contextmanager
from os import environ
from pathlib import Path
from .util.exceptions import SparrowCommandError
from .util.shell import compose, cmd
from rich import print
from rich.console import Console
import docker
from docker.models.containers import Container
import time
from datetime import datetime
import subprocess
from subprocess import Popen
import asyncio
import typing as T
import sys

environ.setdefault("DOCKER_HOST", "unix:///var/run/docker.sock")

client = docker.from_env()

console = Console()


def check_database_cluster_version(volume_name: str):
    """
    Check the version of a PostgreSQL cluster in a Docker volume
    under a managed installation of Sparrow.
    """
    cluster_dir = "/var/lib/postgresql/data"
    version_file = Path(cluster_dir) / "PG_VERSION"
    try:
        stdout = client.containers.run(
            "bash",
            f"cat {version_file}",
            volumes={volume_name: {"bind": cluster_dir, "mode": "ro"}},
            remove=True,
            stdout=True,
        )
    except docker.errors.ContainerError:
        return None
    return int(stdout.decode("utf-8").strip())


version_images = {11: "mdillon/postgis:11", 14: "postgis/postgis:14-3.3"}


def database_cluster_version(cfg):
    cluster_volume_name = cfg.project_name + "_db_cluster"
    return check_database_cluster_version(cluster_volume_name)


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
        res = container.exec_run("pg_isready", user="postgres")
        is_ready = res.exit_code == 0
    time.sleep(1)
    log_step(container)
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
            remove=remove,
            auto_remove=remove,
            environment=environment,
            volumes={data_volume: {"bind": "/var/lib/postgresql/data", "mode": "rw"}},
            user="postgres",
        )
        wait_for_cluster(container)
        yield container
    finally:
        print(f"Stopping database cluster {image}...")
        container.stop()


def check_database_exists(container: Container, db_name: str) -> bool:
    res = container.exec_run(f"psql -U postgres -lqt", stdout=True, demux=True)
    if res.exit_code != 0:
        return False
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
        user="postgres",
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
        '-c "cd /old ; cp -av . /new"',
        volumes={old_name: {"bind": "/old"}, new_name: {"bind": "/new"}},
        remove=True,
    )


def ensure_empty_docker_volume(volume_name: str):
    """
    Ensure that a Docker volume does not exist.
    """
    try:
        client.volumes.get(volume_name).remove()
    except docker.errors.NotFound:
        pass
    return client.volumes.create(name=volume_name)


def upgrade_database_cluster(cfg):
    """
    Upgrade a PostgreSQL cluster in a Docker volume
    under a managed installation of Sparrow.
    """
    cluster_volume_name = cfg.project_name + "_db_cluster"
    cluster_new_name = cfg.project_name + "_db_cluster_new"

    current_version = database_cluster_version(cfg)
    if current_version == cfg.postgres_supported_version:
        print("Database cluster is already up to date.")
        return

    print(current_version)
    if current_version not in version_images:
        raise SparrowCommandError("No upgrade path available")

    if cfg.postgres_supported_version not in version_images:
        raise SparrowCommandError("Target PostgreSQL version is not supported")

    # Create the volume for the new cluster
    dest_volume = ensure_empty_docker_volume(cluster_new_name)

    print(
        f"Upgrading database cluster from version {current_version} to {cfg.postgres_supported_version}..."
    )

    # Stop the database
    compose("down")

    with database_cluster(
        version_images[current_version], cluster_volume_name
    ) as source, database_cluster(
        version_images[cfg.postgres_supported_version],
        dest_volume.name,
        environment={"POSTGRES_HOST_AUTH_METHOD": "trust"},
    ) as target:
        # Dump the database
        time.sleep(2)

        # Check if the database exists
        dbname = "sparrow"
        if check_database_exists(source, dbname):
            print(f"Database {dbname} exists in source cluster")
        else:
            print(f"Database {dbname} does not exist in source, skipping dump.")
            return

        n_tables = count_database_tables(source, dbname)

        print("Creating database")

        res = target.exec_run("createdb -U postgres sparrow", user="postgres")
        print(res)

        if not check_database_exists(target, dbname):
            raise SparrowCommandError("Database not created")

        print("Dumping database...")

        # Run PG_Restore asynchronously
        pg_restore(source, target)

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

    time.sleep(1)

    # Remove the old volume
    backup_volume_name = cluster_volume_name + "_backup"
    console.print(f"Backing up old volume to {backup_volume_name}", style="bold")
    ensure_empty_docker_volume(backup_volume_name)
    replace_docker_volume(cluster_volume_name, backup_volume_name)

    console.print(
        f"Moving contents of new volume to {cluster_volume_name}", style="bold"
    )
    replace_docker_volume(cluster_new_name, cluster_volume_name)
    client.volumes.get(cluster_new_name).remove(force=True)

    console.print("Done!", style="bold green")


# Run in asyncio


async def _pg_restore(source: Container, target: Container):
    source = await asyncio.create_subprocess_exec(
        "docker",
        "exec",
        "-i",
        "-u",
        "postgres",
        source.name,
        "pg_dump",
        "-Fc",
        "--superuser=postgres",
        "-U",
        "postgres",
        "sparrow",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    proc = await asyncio.create_subprocess_exec(
        "docker",
        "exec",
        "-i",
        "-u",
        "postgres",
        target.name,
        "pg_restore",
        "-U",
        "postgres",
        "-d",
        "sparrow",
        stdin=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    await asyncio.gather(
        asyncio.create_task(enqueue(source.stdout, proc.stdin)),
        asyncio.create_task(dequeue(source.stderr)),
        asyncio.create_task(dequeue(proc.stderr)),
    )


def pg_restore(source: Container, target: Container):
    loop = asyncio.get_event_loop()
    task = _pg_restore(source, target)
    loop.run_until_complete(task)
    loop.close()


async def enqueue(in_stream: asyncio.StreamReader, out_stream: asyncio.StreamWriter):
    nbytes = 0
    i = 0
    async for line in in_stream:
        nbytes += len(line)
        i += 1
        if i % 100 == 0:
            print(f"Dumped {nbytes/1_000_000} MB        ", end="\r")
        out_stream.write(line)
        await out_stream.drain()
    out_stream.close()


async def dequeue(stream: asyncio.StreamReader):
    async for line in stream:
        console.print(line.decode("utf-8"), style="dim")
