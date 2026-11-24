import sys
from importlib.metadata import entry_points
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from os import environ
from pathlib import Path

# isort: off
# Plugins import one another; this order avoids import cycles
from ..task_manager import SparrowTaskManager
from ..api import APIv2Plugin
from ..plugins import SparrowPluginManager
from ..import_helpers import InterfacePlugin
from ..auth import AuthPlugin
from ..ext import HeartbeatPlugin
from ..tags import Tags
from ..open_search import OpenSearch
from ..logs import get_logger
from ..import_data import ImportDataPlugin
from ..users import UserManagementPlugin
from ..import_helpers.pipelines import PipelinesPlugin

# isort: on

log = get_logger(__name__)


def _import_plugin_directory():
    """Make a lab's plugin directory importable as `sparrow_plugins`, as it is
    when mounted into a container, for commands run on the lab's own machine."""
    plugin_dir = environ.get("SPARROW_PLUGIN_DIR")
    if plugin_dir is None or "sparrow_plugins" in sys.modules:
        return
    init = Path(plugin_dir) / "__init__.py"
    if not init.is_file() or find_spec("sparrow_plugins") is not None:
        return
    spec = spec_from_file_location(
        "sparrow_plugins", init, submodule_search_locations=[plugin_dir]
    )
    module = module_from_spec(spec)
    sys.modules["sparrow_plugins"] = module
    spec.loader.exec_module(module)


def prepare_plugin_manager(app):
    import core_plugins

    mgr = SparrowPluginManager()
    mgr.add_all(
        APIv2Plugin,
        AuthPlugin,
        HeartbeatPlugin,
        InterfacePlugin,
        PipelinesPlugin,
        Tags,
        ImportDataPlugin,
        OpenSearch,
        UserManagementPlugin,
        SparrowTaskManager,
    )
    # GraphQL is disabled for now
    mgr.add_module(core_plugins)

    # A lab's own code, installed as a package that names its plugins:
    #   [project.entry-points."sparrow.plugins"]
    #   my-lab = "my_lab.plugins"
    for entry_point in entry_points(group="sparrow.plugins"):
        loaded = entry_point.load()
        if isinstance(loaded, type):
            mgr.add(loaded)
        else:
            mgr.add_module(loaded)

    # ...or mounted as a `sparrow_plugins` directory, which may not be there.
    try:
        _import_plugin_directory()
        import sparrow_plugins

        mgr.add_module(sparrow_plugins)
    except ModuleNotFoundError as err:
        log.info(f"No external Sparrow plugins ({err})")

    mgr.finalize(app)
    return mgr
