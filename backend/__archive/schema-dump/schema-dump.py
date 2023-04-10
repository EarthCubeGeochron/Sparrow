#!/usr/bin/env python

from sparrow.database import Database
from sparrow.loader import model_interface
import dill

from macrostrat.database.mapper import DatabaseModelCache

db = Database("postgresql:///sparrow_test")

db.automap()

# Session = model_interface(db.model.session)

# with open("db-models.pickle", "wb") as f:
#     dill.dump(Session, f)

cache_builder = DatabaseModelCache(cache_file="./db-models.pickle")
cache_builder._cache_database_map(metadata=db.mapper.automap_base.metadata)
