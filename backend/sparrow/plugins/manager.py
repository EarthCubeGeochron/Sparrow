from toposort import toposort_flatten
from .base import SparrowPlugin, SparrowPluginError


class SparrowPluginManager(object):
    """
    Storage class for plugins. Currently, we enforce a single
    phase of plugin loading, ended by a call to `finished_loading_plugins`.
    Hooks can be run afterwards. This removes the risk of some parts of the
    application performing actions before all plugins are initialized.
    """

    def __init__(self):
        self.__init_store = []
        self.__store = None

    def __iter__(self):
        yield from self.__store

    @property
    def is_ready(self):
        return self.__store is not None

    def add(self, plugin):
        try:
            self.__init_store.append(plugin)
        except AttributeError:
            raise SparrowPluginError(
                "Cannot add plugins after " "Sparrow is finished loading."
            )

    def order_plugins(self, store=None):
        store = store or self.__store
        struct = {p.name: set(p.dependencies) for p in store}
        map = {p.name: p for p in store}
        res = toposort_flatten(struct)
        return {map[k] for k in res}

    def __load_plugin(self, plugin_class, app):
        try:
            assert issubclass(plugin_class, SparrowPlugin)
        except AssertionError:
            raise SparrowPluginError(
                "Sparrow plugins must be a " "subclass of SparrowPlugin"
            )
        return plugin_class(app)

    def finalize(self, app):
        candidate_store = self.order_plugins(self.__init_store)

        self.__store = []
        for plugin in candidate_store:
            self.__store.append(self.__load_plugin(plugin, app))

        self.__init_store = None

    def get(self, name: str) -> SparrowPlugin:
        """Get a plugin object, given its name."""
        for plugin in self.__store:
            if plugin.name == name:
                return plugin
        raise AttributeError(f"Plugin {name} not found")
