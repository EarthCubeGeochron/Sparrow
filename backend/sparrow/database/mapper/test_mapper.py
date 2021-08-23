from . import SparrowDatabaseMapper


def test_db_mapper_cache(db):
    db.mapper._cache_database_map()
    new_mapper = SparrowDatabaseMapper(db)
    assert new_mapper.loaded_from_cache
    assert hasattr(new_mapper._models, "user")
