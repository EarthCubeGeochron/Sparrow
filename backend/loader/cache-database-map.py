#!python

from macrostrat.database import Database
from macrostrat.database.mapper import DatabaseMapper, DatabaseModelCache

# environ["SPARROW_SECRET_KEY"] = "test-sparrow"

# cmd("sparrow compose up -d db")
uri = "postgresql://postgres@localhost:54321/sparrow"
# wait_for_database(uri)

# cmd("sparrow init")


db = Database(uri)

mapper = DatabaseMapper(db)
mapper.reflect_database(use_cache=False)

cache_builder = DatabaseModelCache(
    cache_file="./sparrow/loader/sparrow-db-models.pickle"
)

cache_builder._cache_database_map(mapper.automap_base.metadata)
