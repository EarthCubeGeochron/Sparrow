from .base import DatasheetAPI
from sparrow.plugins import SparrowCorePlugin


class DatasheetPlugin(SparrowCorePlugin):
    name = "datasheet"

    def on_api_initialized_v2(self, api):
        # TODO: lock this down to authorized users
        api.mount("/datasheet", DatasheetAPI, name="datasheet_api")
