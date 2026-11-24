from importlib.metadata import entry_points

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
        import sparrow_plugins

        mgr.add_module(sparrow_plugins)
    except ModuleNotFoundError as err:
        log.info("Could not load external Sparrow plugins.")
        log.exception(err)

    mgr.finalize(app)
    return mgr
