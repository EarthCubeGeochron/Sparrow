from contextvars import ContextVar
from .logs import get_logger

log = get_logger(__name__)


class SparrowContext:
    """Sparrow's application context floats outside of the server, cli, etc.
    and holds global objects and configuration.
    """

    def __init__(self, flask_app, *args, **kwargs):
        self.v1_app = flask_app
        super().__init__(*args, **kwargs)

    @property
    def database(self):
        return self.v1_app.database

    @property
    def plugins(self):
        return self.v1_app.plugins


_sparrow_context: ContextVar[SparrowContext] = ContextVar(
    "sparrow-context", default=None
)


def _setup_context(v1_app):
    log.debug("Setting up application context")
    ctx = SparrowContext(v1_app)
    _sparrow_context.set(ctx)


def app_context() -> SparrowContext:
    return _sparrow_context.get()
