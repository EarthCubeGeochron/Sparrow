from click import echo, style
from os import environ
from flask import Flask, send_from_directory
from sqlalchemy.engine.url import make_url
from ..encoders import JSONEncoder
from ..api.v1 import APIv1
from ..plugins import SparrowPluginManager, SparrowPlugin, SparrowCorePlugin
from ..interface import InterfacePlugin
from ..auth import AuthPlugin

# from .graph import GraphQLPlugin
from ..web import WebPlugin
from ..logs import get_logger

log = get_logger(__name__)


def echo_error(message, obj=None, err=None):
    if obj is not None:
        message += " " + style(str(obj), bold=True)
    log.error(message)
    if err is not None:
        log.error("  " + str(err))


class App(Flask):
    """
    Sparrow's Flask app is in the process of being removed from the core of the
    system in favor of a new application object based on Starlette.
    """

    def __init__(self, base_app, *args, **kwargs):
        # Setup config as suggested in http://flask.pocoo.org/docs/1.0/config/
        cfg = kwargs.pop("config", None)
        verbose = kwargs.pop("verbose", True)
        super().__init__(*args, **kwargs)
        self.base_app = base_app
        self.verbose = verbose

        self.config.from_object("sparrow.app.default_config")
        if cfg is None:
            cfg = environ.get("SPARROW_BACKEND_CONFIG", None)
        try:
            self.config.from_pyfile(cfg)
        except RuntimeError as err:
            log.info("No lab-specific configuration file found.")

        dburl = self.config.get("DATABASE")
        self.db_url = make_url(dburl)
        self.dbname = self.db_url.database

    @property
    def db(self):
        return self.base_app.db

    @property
    def database(self):
        if self.base_app.db is None:
            self.base_app.setup_database()
        return self.base_app.db

    def run_hook(self, *args, **kwargs):
        self.base_app.run_hook(*args, **kwargs)
