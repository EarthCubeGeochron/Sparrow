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


def check_if_tables_exist(db_conn):
    engine = create_engine(db_conn)
    conn = engine.connect()
    res = conn.execute(
        "SELECT EXISTS (SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'datum')"
    )
    print(res)
