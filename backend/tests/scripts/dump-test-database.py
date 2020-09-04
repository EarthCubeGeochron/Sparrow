#!/usr/bin/env python
"""
Initialize database and dump data into it.
"""
import sys
from sparrow.util import relative_path
from sparrow.app import App

# Add testing files to path
# sys.path.append(relative_path(__file__, ".."))

# from test_dz_import import import_dz_test_data

app = App(__name__)
app.config["DATABASE"] = sys.argv[1]
app.database.initialize()

# dz_data = import_dz_test_data()
# app.database.load_data("session", dz_data)
