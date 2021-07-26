from ..api import APIv2Plugin
from ..legacy.api_v1 import APIv1Plugin
from ..plugins import SparrowPluginManager
from ..interface import InterfacePlugin
from ..auth import AuthPlugin
from ..ext.pychron import PyChronImportPlugin
from ..datasheet import DatasheetPlugin
from ..project_edits import ProjectEdits
from ..ext import HeartbeatPlugin
from ..ext.data_validation import DataValidationPlugin
from ..metrics_endpoint import MetricsEndpoint
from ..tags import Tags
from sparrow.open_search import OpenSearch
from ..import_helpers.api import ImportTrackerPlugin
from ..web import WebPlugin
from ..logs import get_logger
from ..import_data import ImportDataPlugin
from ..users import UserManagementPlugin

log = get_logger(__name__)


def prepare_plugin_manager(app):
    import core_plugins

    mgr = SparrowPluginManager()
    mgr.add_all(
        APIv1Plugin,
        APIv2Plugin,
        AuthPlugin,
        WebPlugin,
        HeartbeatPlugin,
        InterfacePlugin,
        PyChronImportPlugin,
        DatasheetPlugin,
        # ProjectEdits,
        DataValidationPlugin,
        MetricsEndpoint,
        Tags,
        ImportDataPlugin,
        OpenSearch,
        ImportTrackerPlugin,
        UserManagementPlugin,
    )
    # GraphQL is disabled for now
    # self.plugins.add(GraphQLPlugin)
    mgr.add_module(core_plugins)

    # Try to import external plugins, but they might not be defined.
    try:
        import sparrow_plugins

        mgr.add_module(sparrow_plugins)
    except ModuleNotFoundError as err:
        log.info("Could not load external Sparrow plugins.")
        log.info(err)

    mgr.finalize(app)
    return mgr
