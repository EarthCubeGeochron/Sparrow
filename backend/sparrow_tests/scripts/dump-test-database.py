#!/usr/bin/env python
"""
Initialize database and dump data into it.
"""
from sparrow.app import App
from sparrow_tests.helpers.database import testing_database
from sparrow_tests.test_dz_import import import_dz_test_data

with testing_database("sparrow_test_1") as engine:
    app = App(__name__)
    app.database.initialize()

    dz_data = import_dz_test_data()
    app.database.load_data("session", dz_data)
