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
from sparrow_tests.fixtures import basic_project
import logging

log = get_logger(level=logging.WARNING, handler=console_handler)


conn = "postgresql://postgres@db:5432/sparrow_test_1"
with redirect_stdout(stderr), testing_database(conn) as engine:
    # Re-initialize app
    app = App(__name__)
    app.database.initialize()
    app.load()
    app.load_phase_2()

    logging.getLogger("sparrow.interface.schema").setLevel(logging.ERROR)

    project = app.database.load_data(
        "project", basic_project, session=app.database.session
    )

    dz_data = import_dz_test_data()
    session = app.database.load_data("session", dz_data)
    sample_data = {
        "name": "F-90",
        "location": {"type": "Point", "coordinates": [-24.340, 16.108]},
        "elevation": 1700,
        "location_precision": 150,
    }
    sample = app.database.load_data("sample", sample_data)

    # Bind models together...
    # We should be able to do this in the import, but we can't yet
    sample.session_collection = [session]
    project.session_collection = [session]

    app.database.session.add(sample)
    app.database.session.add(project)
    app.database.session.commit()

    # Prepare for dump
    app.database.engine.execute("TRUNCATE TABLE spatial_ref_sys")

    dbargs = connection_args(engine)
    run("pg_dump", "-Fc", dbargs, engine.url.database, stdout=stdout)
