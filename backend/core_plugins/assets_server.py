"""
The asset server plugin allows serving arbitrary content
from a directory in the Sparrow server container,
specified by the SPARROW_ASSET_DIRECTORY environment variable.
"""

from os import environ

from starlette.staticfiles import StaticFiles

from sparrow.core.plugins import SparrowCorePlugin


class AssetsServerPlugin(SparrowCorePlugin):
    name = "assets-server"

    def on_asgi_setup(self, app):
        assets = environ.get("SPARROW_ASSETS_DIRECTORY", None)
        if assets is not None:
            self.app.mount("/assets", StaticFiles(assets))
