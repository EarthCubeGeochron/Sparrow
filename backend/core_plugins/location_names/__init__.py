import click
from sparrow.plugins import SparrowPlugin

class LocationNamesPlugin(SparrowPlugin):
    name = "location-names"
    def on_setup_cli(self, cli):
        cli.add_command(self.cli)

    @click.command(name='update-location-names')
    def cli(self, download=False):
        """
        Update location names
        """
        pass
