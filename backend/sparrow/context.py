from contextvars import ContextVar
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


def get_sparrow_app():
    from .app.base import Sparrow

    val = _sparrow_context.get()
    if val is None:
        app = Sparrow()
        _setup_context(app)
        return app
    return val.app


def get_database():
    return get_sparrow_app().database