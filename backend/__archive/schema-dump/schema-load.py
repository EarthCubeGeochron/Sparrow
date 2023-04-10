#!/usr/bin/env python
import IPython
from os import environ

from macrostrat.database.mapper import DatabaseModelCache
from macrostrat.database.mapper.utils import (
    _classname_for_table,
    name_for_collection_relationship,
    name_for_scalar_relationship,
)
from sparrow.database.mapper import _gen_relationship

environ["SPARROW_CACHE_DATABASE_MODELS"] = "1"
environ["SPARROW_DATABASE_MODEL_CACHE_PATH"] = "./db-models.pickle"

cacher = DatabaseModelCache(cache_file="./db-models.pickle")
cacher._load_database_map()
base = cacher.automap_base()

kwargs = dict(
    name_for_scalar_relationship=name_for_scalar_relationship,
    name_for_collection_relationship=name_for_collection_relationship,
    classname_for_table=_classname_for_table,
    generate_relationship=_gen_relationship,
)

for schema in ["vocabulary", "core_view", "tags", "public"]:
    base.prepare(None, schema="schema", **kwargs)

IPython.embed()
