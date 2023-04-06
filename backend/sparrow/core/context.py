from contextvars import ContextVar
from os import name
from .logs import get_logger

log = get_logger(__name__)


class SparrowContext:
    """Sparrow's application context floats outside of the server, cli, etc.
    and holds global objects and configuration.
    """

    def __init__(self, app, *args, **kwargs):
        self.app = app
        super().__init__(*args, **kwargs)

    @property
    def database(self):
        return self.app.database

    @property
    def plugins(self):
        return self.app.plugins


_sparrow_context: ContextVar[SparrowContext] = ContextVar(
    "sparrow-context", default=None
)


def _setup_context(app):
    log.debug("Setting up application context")
    ctx = SparrowContext(app)
    _sparrow_context.set(ctx)


def app_context() -> SparrowContext:
    return _sparrow_context.get()


def get_app(create=True):
    from .app.base import Sparrow

    val = _sparrow_context.get()
    if val is None and create:
        app = Sparrow()
        _setup_context(app)
        return app
    if val is None or val.app is None:
        raise ValueError("Sparrow application is not created yet.")
    return val.app


# Support a legacy signature
get_sparrow_app = get_app


def get_database():
    return get_app().database


def get_plugin(name: str):
    app = get_app(create=False)
    return app.plugins.get(name)
