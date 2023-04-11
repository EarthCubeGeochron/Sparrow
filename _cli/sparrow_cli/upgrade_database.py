"""
Scripts for upgrading the database cluster if it is out of date.
"""
from macrostrat.utils import get_logger
from macrostrat.dinosaur import upgrade_cluster

log = get_logger(__name__)


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
