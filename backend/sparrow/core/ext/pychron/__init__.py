from json import JSONDecodeError, loads
from os import environ, path
from pathlib import Path

from sparrow.pipelines import Pipeline

from .json_transformer import PyChronJSONImporter
from .repo_crawler import PyChronRepoCrawler, iare, latest_ia_files


class PyChronPipeline(Pipeline):
    """Reads PyChron interpreted age files from clones of PyChron's data
    repositories. `sync_repositories` fetches them; reading needs no network."""

    name = "pychron"
    file_type = "PyChron Interpreted Age"
    transformer = PyChronJSONImporter()

    def discover(self, root):
        root = Path(root)
        if root.is_file():
            yield root
            return
        # Only the latest interpreted age of each group
        yield from latest_ia_files(root)

    def source_url(self, path):
        return _source_urls.get(str(path))

    def read(self, path):
        try:
            data = loads(Path(path).read_text())
        except JSONDecodeError as err:
            raise ValueError(f"Invalid JSON: {err}")
        yield self.transformer.build_session(data, filename=str(path))


# Remote locations of files fetched by `sync_repositories`
_source_urls: dict[str, str] = {}


def sync_repositories(remote, repo_names, local_root=None) -> Path:
    """Clone or update PyChron data repositories, returning where they are."""
    if local_root is None:
        local_root = path.join(environ["SPARROW_DATA_DIR"], ".pychron-repo-cache")
    crawler = PyChronRepoCrawler(remote, repo_names, local_root=local_root)
    for _uid, local_path, remote_url in crawler.scan():
        _source_urls[str(local_path)] = remote_url
    return Path(local_root)
