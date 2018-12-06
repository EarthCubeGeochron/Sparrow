import json

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta

from .util import run_sql_file as __run_sql_file

metadata = MetaData()

class Database:
    def __init__(self, cfg):
        self.engine = create_engine(cfg)
        metadata.create_all(bind=self.engine)
        self.meta = metadata
        self.session = sessionmaker(bind=self.engine)()

    def exec_sql(self, *args):
        __run_sql_file(self.session, *args)
