from pandas import read_sql
from click import secho
from sqlalchemy.exc import ProgrammingError

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
        for i in ["SELECT", "INSERT","UPDATE","CREATE", "DROP","DELETE"]:
            if not line.startswith(i):
                continue
            start = line.split("(")[0].strip()
            secho(start, **kwargs)
            return


def run_sql_file(db, sql_file):
    sql = open(sql_file).read()
    queries = sql.split(';')
    conn = db.connect()
    for q in queries:
        try:
            sql = q.strip()
            conn.execute(sql)
            pretty_print(sql, dim=True)
        except Exception as err:
            pretty_print(sql, fg='red', dim=True, nl=False)
            secho(err.message, fg='red')
    conn.close()


