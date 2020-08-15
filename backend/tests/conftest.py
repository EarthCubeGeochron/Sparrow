from sparrow.app import App
from sqlalchemy.orm import sessionmaker, scoped_session
from pytest import fixture

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
