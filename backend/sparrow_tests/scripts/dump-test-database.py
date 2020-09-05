#!/usr/bin/env python
"""
Initialize database and dump data into it.
"""
from sparrow.app import App
from sparrow_tests.helpers.database import testing_database, connection_args
from sparrow_tests.test_dz_import import import_dz_test_data
from sparrow.util import run
from sys import stderr, stdout
from contextlib import redirect_stdout
from sparrow.logs import console_handler, get_logger
import logging

log = get_logger(level=logging.DEBUG, handler=console_handler)

with redirect_stdout(stderr), testing_database(
    "postgresql://postgres@db:5432/sparrow_test_1"
) as engine:
    app = App(__name__)
    app.database.initialize()
    app.load_phase_2()

    dz_data = import_dz_test_data()
    app.database.load_data("session", dz_data)
    dbargs = connection_args(engine)
    run("pg_dump", "-Fc", dbargs, engine.url.database, stdout=stdout)
