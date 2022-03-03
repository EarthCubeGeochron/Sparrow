from re import U
from . import BaseModel, SparrowDatabaseMapper


def test_db_mapper_cache(db):
    db_mapper = BaseModel.builder
    db_mapper._cache_database_map(BaseModel.metadata)
    new_base = db_mapper()

    mapper = SparrowDatabaseMapper(db, reflect=False)
    mapper.automap_base = new_base
    mapper.reflect_database(use_cache=True)

    assert new_base.loaded_from_cache
