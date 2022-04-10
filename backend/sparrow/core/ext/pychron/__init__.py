from json.decoder import JSONDecodeError
from sparrow.import_helpers.util import SparrowImportError
from click import command, secho, option
from sparrow.core.plugins.base import SparrowPlugin
from sparrow.import_helpers import BaseImporter
from os import path, environ
from json import loads, JSONDecodeError
from rich import print

from sparrow.core.context import get_database
from .json_transformer import PyChronJSONImporter
from .repo_crawler import PyChronRepoCrawler


class PyChronImporter(BaseImporter):
    _importer = PyChronJSONImporter()
    file_type = "PyChron Interpreted Age"

    def import_all(self, remote, repo_names, **kwargs):
        local_root = path.join(environ["SPARROW_DATA_DIR"], ".pychron-repo-cache")
        pr = PyChronRepoCrawler(remote, repo_names, local_root=local_root)
        for (uid, local_path, remote_url) in pr.scan():
            self._import_datafile(
                local_path,
                rec=None,
                extra_data=dict(remote_url=remote_url, pychron_id=uid),
            )

    def set_source_url(self, fn, extra_data={}):
        uri = extra_data.get("remote_url")
        return uri

    def import_datafile(self, fn, rec, **kwargs):
        secho(f"importing file={fn}", dim=True)
        with open(fn, "r") as f:
            contents = f.read()
        try:
            json_data = loads(contents)
        except JSONDecodeError as err:
            print("Could not read json")
            print(contents)
            raise SparrowImportError(f"Invalid JSON")
        res = self._importer.import_file(json_data, filename=fn)
        model = self.db.load_data("session", res)
        yield model
