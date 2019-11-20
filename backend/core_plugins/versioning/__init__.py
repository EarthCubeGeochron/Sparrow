from sparrow.plugins import SparrowCorePlugin

class VersioningPlugin(SparrowCorePlugin):
    name = "versioning"
    def on_core_tables_initialized(self, db):
        print("SSSSS")
