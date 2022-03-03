from . import BaseModel


# def test_db_mapper_cache(db):
#     db_mapper = BaseModel.builder
#     db_mapper._cache_database_map(db.metadata)
#     new_base = db_mapper()
#     new_base.prepare(engine=db.engine)

#     # new_mapper = SparrowDatabaseMapper(db)
#     # assert new_mapper.loaded_from_cache
#     # assert hasattr(new_mapper._models, "user")
