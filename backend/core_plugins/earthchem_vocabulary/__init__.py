from sparrow.plugins import SparrowPlugin

# Basic shim plugin that loads an external CLI
class EarthChemVocabularyPlugin(SparrowPlugin):
    name = "earthchem-vocabulary"
    sparrow_version = ">=1.0"

    def on_setup_cli(self, cli):
        from .cli import import_earthchem

        cli.add_command(import_earthchem)
