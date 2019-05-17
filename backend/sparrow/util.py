import psycopg2
import os
from os import path
from pandas import read_sql
from click import secho
from sqlalchemy.exc import ProgrammingError, IntegrityError
from pathlib import Path
from contextlib import contextmanager
from sqlparse import split, format

def run_query(db, filename_or_query, **kwargs):
    """
    Run a query on a SQL database (represented by
    a SQLAlchemy database object) and turn it into a
    `Pandas` dataframe.
    """

    if "SELECT" in str(filename_or_query):
        # We are working with a query string instead of
        # an SQL file.
        sql = filename_or_query
    else:
        with open(filename_or_query) as f:
            sql = f.read()

    return read_sql(sql,db,**kwargs)

def pretty_print(sql, **kwargs):
    for line in sql.split("\n"):
        for i in ["SELECT", "INSERT","UPDATE","CREATE", "DROP","DELETE", "ALTER"]:
            if not line.startswith(i):
                continue
            start = line.split("(")[0].strip().rstrip(';').replace(" AS","")
            secho(start, **kwargs)
            return

def run_sql(session, sql):
    queries = split(sql)
    for q in queries:
        sql = format(q, strip_comments=True).strip()
        if sql == '':
            continue
        try:
            session.execute(sql)
            session.commit()
            pretty_print(sql, dim=True)
        except (ProgrammingError,IntegrityError) as err:
            err = str(err.orig).strip()
            dim = "already exists" in err
            session.rollback()
            pretty_print(sql,
                fg=None if dim else "red",
                dim=True)
            if dim: err = "  "+err
            secho(err, fg='red', dim=dim)

def run_sql_file(session, sql_file):
    sql = open(sql_file).read()
    run_sql(session, sql)

def relative_path(base, *parts):
    if not path.isdir(base):
        base = path.dirname(base)
    return path.join(base, *parts)

@contextmanager
def working_directory(pathname, *args):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    fn = path.realpath(pathname)
    if not path.isdir(fn):
        fn = path.dirname(fn)
    fn = path.abspath(path.join(fn, *args))
    os.chdir(fn)
    try:
        yield
    finally:
        os.chdir(prev_cwd)
