from click import secho
from sqlalchemy.exc import ProgrammingError, IntegrityError
from sqlparse import split, format
from sqlalchemy.sql import ClauseElement
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy_utils import create_database, database_exists, drop_database
from sparrow_utils import cmd, get_logger
from sqlalchemy.dialects import postgresql
from time import sleep, perf_counter
from click import echo
from dataclasses import dataclass

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


def prettify(sql):
    return format(sql, reindent=True, keyword_case="upper")


def stringify_query(query):
    # make sure we use PostgreSQL dialect
    # https://nicolascadou.com/blog/2014/01/printing-actual-sqlalchemy-queries/
    return prettify(str(query.statement.compile(dialect=postgresql.dialect())))


def print_first_line(sql, **kwargs):
    for line in prettify(sql).split("\n"):
        line = line.strip()
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
            session.execute(sql, params=params)
            session.commit()
            print_first_line(sql, dim=True)
        except (ProgrammingError, IntegrityError) as err:
            err = str(err.orig).strip()
            dim = "already exists" in err
            session.rollback()
            print_first_line(sql, fg=None if dim else "red", dim=True)
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


def run_sql_file(session, sql_file):
    sql = open(sql_file).read()
    run_sql(session, sql)


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
    if isinstance(engine, str):
        # We passed a connection url!
        engine = create_engine(engine)
    uri = engine.url
    flags = f"-U {uri.username} -h {uri.host} -p {uri.port}"
    if password := uri.password:
        flags += f" -P {password}"
    return flags, uri.database


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


@dataclass
class QueryInfo:
    exc_time: float
    #statement: Statement
    ## What is "Statement" supposed to be?
 
class QueryLogger:
    """
    Sets up handlers for two events that let us track the execution time of
    queries.
    Based on https://github.com/pallets/flask-sqlalchemy/blob/master/src/flask_sqlalchemy/__init__.py
    """

    def __init__(self, engine):
        self.engine = engine
        event.listen(self.engine, "before_cursor_execute", self.before_cursor_execute)
        event.listen(self.engine, "after_cursor_execute", self.after_cursor_execute)

    def before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        if current_app:
            context._query_start_time = perf_counter()

    def after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        if current_app:
            try:
                queries = _app_ctx_stack.top.sqlalchemy_queries
            except AttributeError:
                queries = _app_ctx_stack.top.sqlalchemy_queries = []

            queries.append(
                _DebugQueryTuple(
                    (
                        statement,
                        parameters,
                        context._query_start_time,
                        perf_counter(),
                        _calling_context(self.app_package),
                    )
                )
            )
