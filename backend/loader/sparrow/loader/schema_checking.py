#!/usr/bin/env python
from typing import Any
from os import environ
from pathlib import Path
from typing import Any
from contextvars import ContextVar


from macrostrat.database.mapper import DatabaseModelCache
from macrostrat.database.mapper.utils import (
    _classname_for_table,
    name_for_collection_relationship,
    name_for_scalar_relationship,
)
from .util import _gen_relationship

_model_cache: ContextVar[Any] = ContextVar("model-cache", default=None)

cache_file = Path(__file__).parent / "sparrow-db-models.pickle"

environ["SPARROW_CACHE_DATABASE_MODELS"] = "1"
environ["SPARROW_DATABASE_MODEL_CACHE_PATH"] = str(cache_file)

cacher = DatabaseModelCache(cache_file=str(cache_file))


def get_automap_base():
    cache = _model_cache.get()
    if cache is not None:
        return cache
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

    _model_cache.set(base)
    return base


def get_model(name):
    base = get_automap_base()
    return getattr(base.classes, name)
