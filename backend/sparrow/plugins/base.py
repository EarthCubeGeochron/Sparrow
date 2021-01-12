class SparrowPluginError(Exception):
    pass


class SparrowPlugin(object):
    dependencies = []
    # A semantic versioning string
    sparrow_version = None
    name = None

    def __init__(self, app):
        self.app = app
        self.db = self.app.db

    def should_enable(self):
        return True


class SparrowCorePlugin(SparrowPlugin):
    pass
