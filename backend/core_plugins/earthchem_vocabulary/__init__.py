from sparrow.plugins import SparrowPlugin

# Basic shim plugin that loads an external CLI
class EarthChemVocabularyPlugin(SparrowPlugin):
    name = "earthchem-vocabulary"

    def on_setup_cli(self, cli):
        from .cli import import_earthchem

        cli.add_command(import_earthchem)
