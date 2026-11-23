import logging
from os import environ

from macrostrat.database.utils import wait_for_database
from pytest import fixture
from requests import Session as RequestsSession
from sqlalchemy import event
from sqlalchemy.orm import Session, scoped_session
from starlette.testclient import TestClient

from sparrow.core.app import Sparrow
from sparrow.core.auth.create_user import _create_user
from sparrow.core.context import _setup_context
from sparrow.tests.helpers.database import testing_database

disable_loggers = ["macrostrat.database.utils"]

# Slow tests are opt-in


# Right now, we run this setup code outside of a fixture so we
# can see the setup output in real time.
testing_db = environ.get(
    "SPARROW_TESTING_DATABASE", "postgresql://postgres@db:5432/sparrow_test"
)
environ["SPARROW_DATABASE"] = testing_db


def pytest_addoption(parser):
    parser.addoption(
        "--include-slow",
        action="store_true",
        dest="slow",
        default=False,
        help="enable slow-decorated tests",
        ## TODO: add option to remove isolated transaction
    )

    parser.addoption(
        "--no-isolation",
        action="store_false",
        dest="use_isolation",
        default=True,
        help="Use database transaction isolation",
    )

    parser.addoption(
        "--teardown",
        action="store_true",
        dest="teardown",
        default=False,
        help="Tear down database after tests run",
    )


def pytest_configure(config):
    if not config.option.slow:
        setattr(config.option, "markexpr", "not slow")

    for logger_name in disable_loggers:
        logger = logging.getLogger(logger_name)
        logger.disabled = True


@fixture(scope="session")
def app(pytestconfig):
    wait_for_database(testing_db)
    with testing_database(testing_db, drop=pytestconfig.option.teardown) as engine:
        _app = Sparrow(debug=True, database=testing_db)
        _app.bootstrap(init=True)
        _setup_context(_app)
        yield _app


def wait_for_pgrest_api(postgrest_url):
    """Wait for the PostgREST API to be available"""
    from time import sleep

    from requests import get

    while True:
        try:
            get(postgrest_url)
        except Exception as err:
            print(err)
            sleep(0.5)
        else:
            break


@fixture(scope="session")
def pg_api():
    """PostgREST API client for testing"""
    postgrest_url = environ.get("SPARROW_POSTGREST_URL")

    if postgrest_url is None:
        raise ValueError("SPARROW_POSTGREST_URL not set")

    wait_for_pgrest_api(postgrest_url)

    class PostgRESTSession(RequestsSession):
        def request(self, method, url, *args, **kwargs):
            if url.startswith("/"):
                url = postgrest_url + url
            return super().request(method, url, *args, **kwargs)

    session = PostgRESTSession()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


@fixture(scope="function")
def statements(db):
    stmts = []

    def catch_queries(conn, cursor, statement, parameters, context, executemany):
        stmts.append(statement)

    event.listen(db.engine, "before_cursor_execute", catch_queries)
    yield stmts
    event.remove(db.engine, "before_cursor_execute", catch_queries)


@fixture(scope="class")
def db(app, pytestconfig, request):
    # https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    use_isolation = pytestconfig.option.use_isolation
    if request.cls is not None:
        use_isolation = getattr(request.cls, "use_isolation", use_isolation)

    if use_isolation:
        connection = app.database.engine.connect()
        transaction = connection.begin()
        # Commits within the session release a SAVEPOINT rather than
        # ending the enclosing transaction
        session = Session(bind=connection, join_transaction_mode="create_savepoint")

        app.database.session = session
        _setup_context(app)

        yield app.database
        session.close()
        transaction.rollback()
        connection.close()
    else:
        app.database.session = scoped_session(app.database._session_factory)
        yield app.database


@fixture(scope="class")
def client(app, db):
    _client = TestClient(app)
    yield _client


@fixture(scope="class")
def token(db, client):
    if db.session.query(db.model.user).get("test") == None:
        user = "test"
        password = "test"

        _create_user(db, user, password)
    res = client.post(
        "/api/v2/auth/login", json={"username": "test", "password": "test"}
    )

    token = res.json()["token"]

    return token
