from sparrow.app import App
from sqlalchemy.orm import sessionmaker, scoped_session
from pytest import fixture
import logging

logging.disable(level=logging.WARNING)

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


app = App(__name__)


@fixture(scope="class")
def db():
    _db = app.database
    connection = _db.session.connection()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    _db.session = scoped_session(session_factory)
    yield _db
    _db.session.close()
    transaction.rollback()
