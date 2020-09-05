#!/usr/bin/env python
"""
Initialize database and dump data into it.
"""
from sparrow.app import App
from sparrow_tests.helpers.database import testing_database, connection_args
from sparrow_tests.test_dz_import import import_dz_test_data
from sparrow.util import run

with testing_database("postgresql://postgres@db:5432/sparrow_test_1") as engine:
    app = App(__name__)
    app.database.initialize()
    app.load()

    dz_data = import_dz_test_data()
    app.database.load_data("session", dz_data)
    dbargs = connection_args(engine)
    run("pg_dump", "-Fc", dbargs, engine.url.database, stdout=_stdout)
