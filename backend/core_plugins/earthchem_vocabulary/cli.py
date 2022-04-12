#!/usr/bin/env python
"""
Import some basic EarthChem vocabularies from
http://www.earthchem.org/resources/vocabularies
for data categorization.

This should be reworked as a plugin,
once a stable plugin system is created.
"""

import pandas as P
from sparrow.database import Database
from sparrow.database.util import run_sql
from os.path import join, realpath, dirname
from click import command, option

__here = dirname(realpath(__file__))
__fixtures = join(__here, "fixtures")


def download_table(category):
    """
    Download fixtures from EarthChem website and cache in this
    repository.

    NOTE: links are currently broken on the EarthChem website (May 2019).
    """
    url = f"http://www.earthchem.org/petdbWeb/search/vocabulary.jsp?category={category}"
    print(url)
    tables = P.read_html(url, index_col=0)  # Returns list of all tables on page
    df = tables[0]
    df.index.names = ["id"]
    df.rename(
        columns={"METHOD_NAME": "description", "DESCRIPTION": "description"},
        inplace=True,
    )
    return df


def write_table(conn, df, name):
    df.to_sql(name, conn, schema="earthchem_vocabulary", if_exists="replace")


def copy_table(conn, category, tbl, download=False):
    fp = join(__fixtures, tbl + ".csv")
    if download:
        df = download_table(category)
        df.to_csv(fp)
    else:
        df = P.read_csv(fp)
    write_table(conn, df, tbl)
    return df


@command(name="import-earthchem")
@option("--download", is_flag=True, default=False)
def import_earthchem(download=False):
    """
    Import EarthChem vocabulary files
    """
    db = Database()
    conn = db.engine

    run_sql(db.session, "CREATE SCHEMA IF NOT EXISTS earthchem_vocabulary")

    units = copy_table(conn, "Unit", "unit", download=download)
    methods = copy_table(conn, "Method", "method", download=download)
    parameters = copy_table(conn, "MeasuredParameter", "parameter", download=download)

    _ = join(__here, "populate-vocabulary.sql")
    db.exec_sql(_)

    run_sql(db.session, "DROP SCHEMA earthchem_vocabulary CASCADE")
