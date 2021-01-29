"""
The asset server plugin allows serving arbitrary content
from a directory in the Sparrow server container,
specified by the SPARROW_ASSET_DIRECTORY environment variable.
"""

from sparrow.plugins import SparrowCorePlugin
from starlette.staticfiles import StaticFiles
from os import environ


class AssetsServerPlugin(SparrowCorePlugin):
    name = "assets-server"

    def on_asgi_setup(self, app):
        assets = environ.get("SPARROW_ASSETS_DIRECTORY", None)
        if assets is not None:
            self.app.mount("/assets", StaticFiles(assets))
