from pytest import fixture
from os import environ
from starlette.testclient import TestClient
from sparrow.app import Sparrow
from sparrow.context import _setup_context
from sparrow.database.util import wait_for_database
from sqlalchemy.orm import Session
from sqlalchemy import event
from .helpers.database import testing_database

# Slow tests are opt-in


# Right now, we run this setup code outside of a fixture so we
# can see the setup output in real time.
testing_db = "postgresql://postgres@db:5432/sparrow_test"
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
        default=True,
        help="Tear down database after tests run",
    )


def pytest_configure(config):
    if not config.option.slow:
        setattr(config.option, "markexpr", "not slow")


@fixture(scope="session")
def app(pytestconfig):
    wait_for_database(testing_db)
    with testing_database(testing_db, drop=pytestconfig.option.teardown) as engine:
        _app = Sparrow(debug=True, database=testing_db)
        _app.bootstrap(init=True)
        _setup_context(_app)
        yield _app


@fixture(scope="function")
def statements(db):
    stmts = []

    def catch_queries(conn, cursor, statement, parameters, context, executemany):
        stmts.append(statement)

    event.listen(db.engine, "before_cursor_execute", catch_queries)
    yield stmts
    event.remove(db.engine, "before_cursor_execute", catch_queries)


@fixture(scope="class")
def db(app, pytestconfig):
    # https://docs.sqlalchemy.org/en/13/orm/session_transaction.html
    # https://gist.github.com/zzzeek/8443477
    if pytestconfig.option.use_isolation:
        connection = app.database.engine.connect()
        transaction = connection.begin()
        session = Session(bind=connection)

        # start the session in a SAVEPOINT...
        # start the session in a SAVEPOINT...
        session.begin_nested()

        # then each time that SAVEPOINT ends, reopen it
        @event.listens_for(session, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:

                # ensure that state is expired the way
                # session.commit() at the top level normally does
                # (optional step)
                session.expire_all()
                session.begin_nested()

        app.database.session = session
        _setup_context(app)

        yield app.database
        session.close()
        transaction.rollback()
        connection.close()
    else:
        yield app.database


@fixture(scope="class")
def client(app, db):
    _client = TestClient(app)
    yield _client
