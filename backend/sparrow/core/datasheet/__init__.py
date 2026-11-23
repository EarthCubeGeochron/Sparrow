from sparrow.core.plugins import SparrowCorePlugin

from .base import DatasheetAPI


class DatasheetPlugin(SparrowCorePlugin):
    name = "datasheet"

    def on_api_initialized_v2(self, api):
        # TODO: lock this down to authorized users
        api.mount("/datasheet", DatasheetAPI, name="datasheet_api")
