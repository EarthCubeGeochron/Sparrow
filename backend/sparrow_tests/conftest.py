from sqlalchemy.orm import sessionmaker, scoped_session
from pytest import fixture
from starlette.testclient import TestClient
from sparrow.app import Sparrow
from sparrow.context import _setup_context

app_ = Sparrow(debug=True)

# Slow tests are opt-in
def pytest_addoption(parser):
    parser.addoption(
        "--include-slow",
        action="store_true",
        dest="slow",
        default=False,
        help="enable slow-decorated tests",
    )


def pytest_configure(config):
    if not config.option.slow:
        setattr(config.option, "markexpr", "not slow")


@fixture(scope="session")
def app():
    return Sparrow()


@fixture(scope="class")
def db(app):
    connection = app.database.session.connection()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    app.database.session = scoped_session(session_factory)
    _setup_context(app)
    yield app.database
    app.database.session.close()
    transaction.rollback()


@fixture
def client():
    _client = TestClient(app_)
    yield _client
