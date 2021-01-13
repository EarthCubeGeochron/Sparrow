from sparrow.context import get_sparrow_app
from sqlalchemy.orm import sessionmaker, scoped_session
from pytest import fixture
from starlette.testclient import TestClient
from sparrow.app import Sparrow
from sparrow.context import _setup_context
from sparrow.startup import wait_for_database
from .helpers.database import testing_database

# Slow tests are opt-in


def pytest_addoption(parser):
    parser.addoption(
        "--include-slow",
        action="store_true",
        dest="slow",
        default=False,
        help="enable slow-decorated tests",
    )

    parser.addoption(
        "--no-isolation",
        action="store_false",
        dest="use_isolation",
        default=True,
        help="Use database transaction isolation",
    )


def pytest_configure(config):
    if not config.option.slow:
        setattr(config.option, "markexpr", "not slow")


@fixture(scope="session")
def app():
    wait_for_database("postgresql://postgres@db:5432/postgres")
    with testing_database("postgresql://postgres@db:5432/sparrow_test"):
        app = Sparrow(debug=True)
        app.bootstrap()
        _setup_context(app)
        yield app


@fixture(scope="class")
def db(app, pytestconfig):
    if pytestconfig.option.use_isolation:
        connection = app.database.session.connection()
        transaction = connection.begin()
        session_factory = sessionmaker(bind=connection)
        app.database.session = scoped_session(session_factory)
        _setup_context(app)
        yield app.database
        app.database.session.close()
        transaction.rollback()
    else:
        yield app.database


@fixture
def client(app):
    _client = TestClient(app)
    yield _client
