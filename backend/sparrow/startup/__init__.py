from sparrow.logs import get_logger
from sqlalchemy import create_engine

log = get_logger(__name__)


def tables_exist(db_conn):
    engine = create_engine(db_conn)
    conn = engine.connect()
    res = conn.execute(
        "SELECT EXISTS (SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'datum')"
    ).scalar()
    return res
