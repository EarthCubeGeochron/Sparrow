from sparrow.logs import get_logger
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from time import sleep

log = get_logger(__name__)


def wait_for_database(db_conn):
    engine = create_engine(db_conn)
    while True:
        try:
            engine.connect()
            log.info("Database is available")
            return
        except OperationalError:
            immediate = False
            log.info("Waiting for database")
            sleep(1)
