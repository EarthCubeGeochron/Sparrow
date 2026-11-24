from sparrow.loader import InterfaceCollection

from ..plugins import SparrowCorePlugin


class InterfacePlugin(SparrowCorePlugin):
    name = "schema-interface"

    def on_database_ready(self, db):
        iface = InterfaceCollection(db.model)
        db.interface = iface
