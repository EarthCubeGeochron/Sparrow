class SparrowPluginError(Exception):
    pass


class SparrowPlugin(object):
    dependencies = []
    name = None

    def __init__(self, app):
        self.app = app
        self.db = self.app.db


class SparrowCorePlugin(SparrowPlugin):
    pass
