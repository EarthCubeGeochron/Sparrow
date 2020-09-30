from click import command, secho, option
from sparrow.plugins.base import SparrowPlugin
from sparrow.import_helpers import BaseImporter
from sparrow.cli.util import with_database
from os import path, environ
from json import load
from rich import print

from .json_transformer import PyChronJSONImporter
from .repo_crawler import PyChronRepoCrawler


class PyChronImporter(BaseImporter):
    _importer = PyChronJSONImporter()
    file_type = "PyChron Interpreted Age"
    _session = None

    def import_all(self, **kwargs):
        name = "NOB-Unknowns"
        remote = "https://github.com/WiscArData"

        self._schema = self.db.interface.session()

        local_root = path.join(environ["SPARROW_CACHE_DIR"], ".pychron-repo-cache")

        pr = PyChronRepoCrawler(name, remote, local_root=local_root)
        file_iter = (f for uid, f in pr.scan())
        self.iterfiles(file_iter, **kwargs)

    def import_datafile(self, fn, rec, **kwargs):
        secho(f"importing file={fn}", dim=True)
        with open(fn, "r") as f:
            res = self._importer.import_file(load(f))
        model = self._schema.load(res, session=self.db.session)
        self.db.session.add(model)
        yield model


@command(name="import-pychron")
@option("--redo", is_flag=True, default=False)
@with_database
def pychron_import_command(db, redo=False):
    """Import PyChron Interpreted Age files."""
    importer = PyChronImporter(db, verbose=True)
    importer.import_all(redo=redo)


class PyChronImportPlugin(SparrowPlugin):
    name = "pychron-importer"

    def on_setup_cli(self, cli):
        cli.add_command(pychron_import_command)
