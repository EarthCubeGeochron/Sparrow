from sparrow.app import App
from sqlalchemy.orm import sessionmaker, scoped_session
from pytest import fixture
from starlette.testclient import TestClient
from sparrow.asgi import app as app_
from sparrow.context import _setup_context


# Slow tests are opt-in
def pytest_addoption(parser):
    parser.addoption(
        "--include-slow",
        action="store_true",
        dest="slow",
        default=False,
        help="enable slow-decorated tests",
        ## TODO: add option to remove isolated transaction
    )


def pytest_configure(config):
    if not config.option.slow:
        setattr(config.option, "markexpr", "not slow")


@fixture(scope="session")
def app():
    return App(__name__)


@fixture(scope="class") ## run before sets of tests. Scopes === how often run, after a class
def db(app):
    # connection = app.database.session.connection()
    # transaction = connection.begin()
    # session_factory = sessionmaker(bind=connection)
    # app.database.session = scoped_session(session_factory)
    # _setup_context(app)
    # yield app.database
    # app.database.session.close()
    # transaction.rollback()
    return app.database


@fixture
def client():
    _client = TestClient(app_)
    yield _client
