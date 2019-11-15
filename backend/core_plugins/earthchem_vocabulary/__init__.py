from sparrow.plugins import SparrowPlugin
from .cli import import_earthchem

class EarthChemVocabularyPlugin(SparrowPlugin):
    name = "earthchem-vocabulary"
    def on_setup_cli(self, cli):
        wrapper = cli.command(name="import-earthchem-vocabulary")
        wrapper(import_earthchem)
