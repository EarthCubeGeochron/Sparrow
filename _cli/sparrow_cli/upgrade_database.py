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
from subprocess import CalledProcessError
import asyncio
import typing as T
import sys
from macrostrat.utils import get_logger
from docker.client import DockerClient

from macrostrat.dinosaur import upgrade_cluster

log = get_logger(__name__)


console = Console()

version_images = {11: "mdillon/postgis:11", 14: "postgis/postgis:14-3.3"}


def upgrade_database_cluster(cfg):
    """
    Upgrade a PostgreSQL cluster in a Docker volume
    under a managed installation of Sparrow.
    """
    cluster_volume_name = cfg.project_name + "_db_cluster"

    upgrade_cluster.upgrade_database_cluster(
        cfg.docker_client,
        cluster_volume_name,
        cfg.postgres_supported_version,
        ["sparrow"],
        version_images=version_images,
    )


# Run in asyncio
