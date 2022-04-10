import sparrow
from toposort import toposort_flatten
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version
from .base import SparrowPlugin, SparrowCorePlugin, SparrowPluginError
from ..logs import get_logger

log = get_logger(__name__)


def handle_compat_error(plugin):
    _error = (
        f"Plugin '{plugin.name}' is incompatible with Sparrow core "
        f"version {sparrow.__version__} (expected {plugin.sparrow_version})"
    )
    log.error(_error)
    if issubclass(plugin, SparrowCorePlugin):
        raise SparrowPluginError(_error)


def handle_load_error(plugin, err):
    _error = f"Could not load plugin '{plugin.name}': {err}"
    log.error(_error)
    if issubclass(plugin, SparrowCorePlugin):
        raise SparrowPluginError(_error)


class SparrowPluginManager(object):
    """
    Storage class for plugins. Currently, we enforce a single
    phase of plugin loading, ended by a call to `finished_loading_plugins`.
    Hooks can be run afterwards. This removes the risk of some parts of the
    application performing actions before all plugins are initialized.
    """

    _hooks_fired = []

    def __init__(self):
        self.__init_store = []
        self.__store = None

    def __iter__(self):
        try:
            yield from self.__store
        except TypeError:
            raise SparrowPluginError("Cannot list plugins until loading is finished.")

    @property
    def is_ready(self):
        return self.__store is not None

    def _is_compatible(self, plugin):
        """Assess package compatibility: https://packaging.pypa.io/en/latest/specifiers.html"""
        if plugin.sparrow_version is None:
            return True
        try:
            spec = SpecifierSet(plugin.sparrow_version, prereleases=True)
        except InvalidSpecifier:
            raise SparrowPluginError(
                f"Plugin '{plugin.name}' specifies an invalid Sparrow compatibility range '{plugin.sparrow_version}'"
            )
        return Version(sparrow.__version__) in spec

    def add(self, plugin):
        if not plugin.should_enable(self):
            return
        if not self._is_compatible(plugin):
            handle_compat_error(plugin)
            return

        try:
            self.__init_store.append(plugin)
        except AttributeError:
            raise SparrowPluginError(
                "Cannot add plugins after Sparrow is finished loading."
            )
        except Exception as err:
            handle_load_error(plugin, err)

    def add_module(self, module):
        for _, obj in module.__dict__.items():
            try:
                assert issubclass(obj, SparrowPlugin)
            except (TypeError, AssertionError):
                continue

            if obj in [SparrowPlugin, SparrowCorePlugin]:
                continue

            self.add(obj)

    def add_all(self, *plugins):
        for plugin in plugins:
            self.add(plugin)

    def order_plugins(self, store=None):
        store = store or self.__store
        for p in store:
            if getattr(p, "name") is None:
                raise SparrowPluginError(
                    f"Sparrow plugin '{p}' must have a name attribute."
                )
        struct = {p.name: set(p.dependencies) for p in store}
        map_ = {p.name: p for p in store}
        res = toposort_flatten(struct, sort=True)
        return {map_[k] for k in res}

    def __load_plugin(self, plugin_class, app):
        if not issubclass(plugin_class, SparrowPlugin):
            raise SparrowPluginError(
                "Sparrow plugins must be a subclass of SparrowPlugin"
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

    def _iter_hooks(self, hook_name):
        method_name = "on_" + hook_name.replace("-", "_")
        for plugin in self.__store:
            method = getattr(plugin, method_name, None)
            if method is None:
                continue
            log.info("  plugin: " + plugin.name)
            yield plugin, method

    def run_hook(self, hook_name, *args, **kwargs):
        self._hooks_fired.append(hook_name)
        for _, method in self._iter_hooks(hook_name):
            method(*args, **kwargs)
