from sparrow.context import get_sparrow_app, get_database


class SparrowPluginError(Exception):
    pass


class SparrowPlugin(object):
    """A base plugin for Sparrow

    sparrow_version can be set to a specifier of valid versions of Sparrow. This may
    become mandatory in a future release of Sparrow.
    """

    dependencies = []
    sparrow_version = None
    name = None

    def __init__(self, app):
        self.app = app
        self.db = self.app.db

    def should_enable(self):
        return True


class SparrowCorePlugin(SparrowPlugin):
    pass
