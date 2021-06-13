from click import secho
from sqlalchemy.exc import ProgrammingError, IntegrityError
from sqlparse import split, format
from sqlalchemy.sql import ClauseElement
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy_utils import create_database, database_exists, drop_database
from sparrow_utils import cmd, get_logger
from time import sleep
from click import echo

log = get_logger(__name__)


def db_session(engine):
    factory = sessionmaker(bind=engine)
    return factory()


def run_query(db, filename_or_query, **kwargs):
    """
    Run a query on a SQL database (represented by
    a SQLAlchemy database object) and turn it into a
    `Pandas` dataframe.
    """
    from pandas import read_sql

    if "SELECT" in str(filename_or_query):
        # We are working with a query string instead of
        # an SQL file.
        sql = filename_or_query
    else:
        with open(filename_or_query) as f:
            sql = f.read()

    return read_sql(sql, db, **kwargs)


def pretty_print(sql, **kwargs):
    for line in sql.split("\n"):
        for i in ["SELECT", "INSERT", "UPDATE", "CREATE", "DROP", "DELETE", "ALTER"]:
            if not line.startswith(i):
                continue
            start = line.split("(")[0].strip().rstrip(";").replace(" AS", "")
            secho(start, **kwargs)
            return


def run_sql(session, sql, params=None):
    queries = split(sql)
    for q in queries:
        sql = format(q, strip_comments=True).strip()
        if sql == "":
            continue
        try:
            session.execute(text(sql), params=params)
            if hasattr(session, "commit"):
                session.commit()
            pretty_print(sql, dim=True)
        except (ProgrammingError, IntegrityError) as err:
            err = str(err.orig).strip()
            dim = "already exists" in err
            if hasattr(session, "rollback"):
                session.rollback()
            pretty_print(sql, fg=None if dim else "red", dim=True)
            if dim:
                err = "  " + err
            secho(err, fg="red", dim=dim)


def _exec_raw_sql(engine, sql):
    """Execute SQL unsafely on an sqlalchemy Engine"""
    try:
        engine.execute(text(sql))
        pretty_print(sql, dim=True)
    except (ProgrammingError, IntegrityError) as err:
        err = str(err.orig).strip()
        dim = "already exists" in err
        pretty_print(sql, fg=None if dim else "red", dim=True)
        if dim:
            err = "  " + err
        secho(err, fg="red", dim=dim)


def run_sql_file(session, sql_file, params=None):
    sql = open(sql_file).read()
    run_sql(session, sql, params=params)


def run_sql_query_file(session, sql_file, params=None):
    sql = open(sql_file).read()
    return session.execute(sql, params)


def get_or_create(session, model, defaults=None, **kwargs):
    """
    Get an instance of a model, or create it if it doesn't
    exist.

    https://stackoverflow.com/questions/2546207
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        instance._created = False
        return instance
    else:
        params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        instance._created = True
        return instance


def get_db_model(db, model_name: str):
    return getattr(db.model, model_name)


@contextmanager
def temp_database(conn_string, drop=True):
    """Create a temporary database and tear it down after tests."""
    if not database_exists(conn_string):
        create_database(conn_string)
    try:
        yield create_engine(conn_string)
    finally:
        if drop:
            drop_database(conn_string)


def connection_args(engine):
    """Get PostgreSQL connection arguments for a engine"""
    _psql_flags = {"-U": "username", "-h": "host", "-p": "port", "-P": "password"}

    if isinstance(engine, str):
        # We passed a connection url!
        engine = create_engine(engine)
    flags = ""
    for flag, _attr in _psql_flags.items():
        val = getattr(engine.url, _attr)
        if val is not None:
            flags += f" {flag} {val}"
    return flags, engine.url.database


def db_isready(engine_or_url):
    args, _ = connection_args(engine_or_url)
    c = cmd("pg_isready", args)
    return c.returncode == 0


def wait_for_database(engine_or_url, quiet=False):
    msg = "Waiting for database..."
    while not db_isready(engine_or_url):
        if not quiet:
            echo(msg)
        log.info(msg)
        sleep(1)